import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import OrderStatus
from app.models.user import User
from app.schemas.common import Message, PaginatedResponse
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=PaginatedResponse[OrderOut])
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: OrderStatus | None = None,
    customer_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = order_service.list_orders(
        db, page=page, page_size=page_size, status=status, customer_id=customer_id
    )
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db),
              _: User = Depends(get_current_user)):
    return order_service.get(db, order_id)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    return order_service.create_order(db, data, current.id)


@router.put("/{order_id}", response_model=OrderOut)
def update_order_status(order_id: uuid.UUID, data: OrderStatusUpdate,
                        db: Session = Depends(get_db),
                        current: User = Depends(get_current_user)):
    return order_service.update_status(db, order_id, data.status, current.id)


@router.delete("/{order_id}", response_model=Message)
def delete_order(order_id: uuid.UUID, db: Session = Depends(get_db),
                 current: User = Depends(get_current_user)):
    order_service.delete(db, order_id, current.id)
    return Message(message="Order deleted")
