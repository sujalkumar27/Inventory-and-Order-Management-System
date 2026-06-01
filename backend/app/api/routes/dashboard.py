import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardResponse)
def stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return dashboard_service.get_dashboard(db)


@router.get("/products/export", tags=["export"])
def export_products_csv(db: Session = Depends(get_db),
                        _: User = Depends(get_current_user)):
    """Bonus: CSV export of the product catalogue."""
    products = db.scalars(
        select(Product).where(Product.is_deleted.is_(False)).order_by(Product.name)
    ).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "sku", "name", "price", "stock_quantity", "created_at"])
    for p in products:
        writer.writerow([p.id, p.sku, p.name, p.price, p.stock_quantity, p.created_at])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )
