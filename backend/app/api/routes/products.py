import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Message, PaginatedResponse
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedResponse[ProductOut])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    sort_by: str = Query("name", pattern="^(name|price|stock_quantity)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    in_stock: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = product_service.list_products(
        db, page=page, page_size=page_size, search=search,
        sort_by=sort_by, order=order, in_stock=in_stock,
    )
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    return product_service.get(db, product_id)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db),
                   current: User = Depends(get_current_user)):
    return product_service.create(db, data, current.id)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: uuid.UUID, data: ProductUpdate,
                   db: Session = Depends(get_db),
                   current: User = Depends(get_current_user)):
    return product_service.update(db, product_id, data, current.id)


@router.delete("/{product_id}", response_model=Message)
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db),
                   current: User = Depends(get_current_user)):
    product_service.delete(db, product_id, current.id)
    return Message(message="Product deleted")
