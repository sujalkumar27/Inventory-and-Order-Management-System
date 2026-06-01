import uuid
from datetime import datetime, timezone

from sqlalchemy import asc, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.utils.audit import record_audit


def _get_active(db: Session, customer_id: uuid.UUID) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer or customer.is_deleted:
        raise NotFoundError("Customer not found")
    return customer


def get(db: Session, customer_id: uuid.UUID) -> Customer:
    return _get_active(db, customer_id)


def list_customers(
    db: Session, *, page: int = 1, page_size: int = 10, search: str | None = None
) -> tuple[list[Customer], int]:
    stmt = select(Customer).where(Customer.is_deleted.is_(False))
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Customer.first_name.ilike(like),
                Customer.last_name.ilike(like),
                Customer.email.ilike(like),
            )
        )
    stmt = stmt.order_by(asc(Customer.first_name))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
    return items, total


def _email_taken(db: Session, email: str, exclude_id: uuid.UUID | None = None) -> bool:
    stmt = select(Customer).where(Customer.email == email, Customer.is_deleted.is_(False))
    if exclude_id:
        stmt = stmt.where(Customer.id != exclude_id)
    return db.scalar(stmt) is not None


def create(db: Session, data: CustomerCreate, user_id: uuid.UUID | None) -> Customer:
    if _email_taken(db, str(data.email)):
        raise ConflictError("Email already exists")
    customer = Customer(**{**data.model_dump(), "email": str(data.email)})
    db.add(customer)
    db.flush()
    record_audit(db, user_id=user_id, action="create",
                 entity_type="customer", entity_id=customer.id)
    db.commit()
    db.refresh(customer)
    return customer


def update(db: Session, customer_id: uuid.UUID, data: CustomerUpdate,
           user_id: uuid.UUID | None) -> Customer:
    customer = _get_active(db, customer_id)
    payload = data.model_dump(exclude_unset=True)
    if "email" in payload:
        payload["email"] = str(payload["email"])
        if _email_taken(db, payload["email"], exclude_id=customer_id):
            raise ConflictError("Email already exists")
    for key, value in payload.items():
        setattr(customer, key, value)
    record_audit(db, user_id=user_id, action="update",
                 entity_type="customer", entity_id=customer.id)
    db.commit()
    db.refresh(customer)
    return customer


def delete(db: Session, customer_id: uuid.UUID, user_id: uuid.UUID | None) -> None:
    customer = _get_active(db, customer_id)
    customer.is_deleted = True
    customer.deleted_at = datetime.now(timezone.utc)
    record_audit(db, user_id=user_id, action="delete",
                 entity_type="customer", entity_id=customer.id)
    db.commit()
