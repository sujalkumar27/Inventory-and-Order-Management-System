import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import Message, PaginatedResponse
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=PaginatedResponse[CustomerOut])
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = customer_service.list_customers(
        db, page=page, page_size=page_size, search=search
    )
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: uuid.UUID, db: Session = Depends(get_db),
                 _: User = Depends(get_current_user)):
    return customer_service.get(db, customer_id)


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)):
    return customer_service.create(db, data, current.id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: uuid.UUID, data: CustomerUpdate,
                    db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)):
    return customer_service.update(db, customer_id, data, current.id)


@router.delete("/{customer_id}", response_model=Message)
def delete_customer(customer_id: uuid.UUID, db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)):
    customer_service.delete(db, customer_id, current.id)
    return Message(message="Customer deleted")
