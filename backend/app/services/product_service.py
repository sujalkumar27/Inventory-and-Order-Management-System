import uuid
from datetime import datetime, timezone

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.audit import record_audit


def _get_active(db: Session, product_id: uuid.UUID) -> Product:
    product = db.get(Product, product_id)
    if not product or product.is_deleted:
        raise NotFoundError("Product not found")
    return product


def get(db: Session, product_id: uuid.UUID) -> Product:
    return _get_active(db, product_id)


def list_products(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    sort_by: str = "name",
    order: str = "asc",
    in_stock: bool | None = None,
) -> tuple[list[Product], int]:
    stmt = select(Product).where(Product.is_deleted.is_(False))

    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.sku.ilike(like)))
    if in_stock is True:
        stmt = stmt.where(Product.stock_quantity > 0)
    elif in_stock is False:
        stmt = stmt.where(Product.stock_quantity <= 0)

    sort_col = {"name": Product.name, "price": Product.price,
                "stock_quantity": Product.stock_quantity}.get(sort_by, Product.name)
    stmt = stmt.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(
        db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    )
    return items, total


def create(db: Session, data: ProductCreate, user_id: uuid.UUID | None) -> Product:
    if db.scalar(select(Product).where(Product.sku == data.sku, Product.is_deleted.is_(False))):
        raise ConflictError("SKU already exists")
    product = Product(**data.model_dump())
    db.add(product)
    db.flush()
    record_audit(db, user_id=user_id, action="create",
                 entity_type="product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product_id: uuid.UUID, data: ProductUpdate,
           user_id: uuid.UUID | None) -> Product:
    product = _get_active(db, product_id)
    payload = data.model_dump(exclude_unset=True)
    if "sku" in payload and payload["sku"] != product.sku:
        if db.scalar(select(Product).where(Product.sku == payload["sku"],
                                           Product.is_deleted.is_(False))):
            raise ConflictError("SKU already exists")
    for key, value in payload.items():
        setattr(product, key, value)
    record_audit(db, user_id=user_id, action="update",
                 entity_type="product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product_id: uuid.UUID, user_id: uuid.UUID | None) -> None:
    product = _get_active(db, product_id)
    product.is_deleted = True
    product.deleted_at = datetime.now(timezone.utc)
    record_audit(db, user_id=user_id, action="delete",
                 entity_type="product", entity_id=product.id)
    db.commit()
