import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    InsufficientInventoryError,
    NotFoundError,
    ValidationAppError,
)
from app.models.customer import Customer
from app.models.inventory_history import InventoryChangeReason, InventoryHistory
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.utils.audit import record_audit


def _record_inventory(db: Session, product: Product, change: int,
                      reason: InventoryChangeReason, reference_id: uuid.UUID) -> None:
    previous = product.stock_quantity
    product.stock_quantity = previous + change
    db.add(
        InventoryHistory(
            product_id=product.id,
            change=change,
            previous_quantity=previous,
            new_quantity=product.stock_quantity,
            reason=reason,
            reference_id=reference_id,
        )
    )


def get(db: Session, order_id: uuid.UUID) -> Order:
    order = db.scalar(
        select(Order)
        .where(Order.id == order_id, Order.is_deleted.is_(False))
        .options(selectinload(Order.items))
    )
    if not order:
        raise NotFoundError("Order not found")
    return order


def list_orders(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    status: OrderStatus | None = None,
    customer_id: uuid.UUID | None = None,
) -> tuple[list[Order], int]:
    stmt = (
        select(Order)
        .where(Order.is_deleted.is_(False))
        .options(selectinload(Order.items))
    )
    if status:
        stmt = stmt.where(Order.status == status)
    if customer_id:
        stmt = stmt.where(Order.customer_id == customer_id)
    stmt = stmt.order_by(Order.order_date.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
    return items, total


def create_order(db: Session, data: OrderCreate, user_id: uuid.UUID | None) -> Order:
    # 1. Validate customer exists.
    customer = db.get(Customer, data.customer_id)
    if not customer or customer.is_deleted:
        raise NotFoundError("Customer not found")

    # Merge duplicate product lines so stock checks are correct.
    requested: dict[uuid.UUID, int] = {}
    for line in data.items:
        requested[line.product_id] = requested.get(line.product_id, 0) + line.quantity

    order = Order(customer_id=customer.id, status=OrderStatus.PENDING, total_amount=Decimal("0"))
    db.add(order)
    db.flush()  # assign order.id

    total = Decimal("0")
    for product_id, quantity in requested.items():
        # 2. Validate product exists.
        product = db.get(Product, product_id)
        if not product or product.is_deleted:
            raise NotFoundError(f"Product {product_id} not found")
        # 3 & 4. Validate quantity & stock.
        if quantity <= 0:
            raise ValidationAppError("Quantity must be greater than zero")
        if product.stock_quantity < quantity:
            # 5. Insufficient -> abort, no order created (rollback below).
            db.rollback()
            raise InsufficientInventoryError("Insufficient inventory")

        unit_price = Decimal(product.price)
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )
        # 6. Deduct inventory + track history.
        _record_inventory(db, product, -quantity, InventoryChangeReason.ORDER, order.id)
        total += unit_price * quantity

    # 7. Total computed automatically.
    order.total_amount = total
    record_audit(db, user_id=user_id, action="create", entity_type="order",
                 entity_id=order.id, detail=f"total={total}")
    db.commit()
    return get(db, order.id)


def update_status(db: Session, order_id: uuid.UUID, new_status: OrderStatus,
                  user_id: uuid.UUID | None) -> Order:
    order = get(db, order_id)
    old_status = order.status

    # Restock when an active order is cancelled.
    if new_status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.get(Product, item.product_id)
            if product:
                _record_inventory(db, product, item.quantity,
                                  InventoryChangeReason.ORDER_CANCELLED, order.id)

    order.status = new_status
    record_audit(db, user_id=user_id, action="update", entity_type="order",
                 entity_id=order.id, detail=f"{old_status.value} -> {new_status.value}")
    db.commit()
    return get(db, order.id)


def delete(db: Session, order_id: uuid.UUID, user_id: uuid.UUID | None) -> None:
    order = get(db, order_id)
    # Restock if the order was not already cancelled.
    if order.status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.get(Product, item.product_id)
            if product:
                _record_inventory(db, product, item.quantity,
                                  InventoryChangeReason.ORDER_CANCELLED, order.id)
    order.is_deleted = True
    order.deleted_at = datetime.now(timezone.utc)
    record_audit(db, user_id=user_id, action="delete", entity_type="order",
                 entity_id=order.id)
    db.commit()
