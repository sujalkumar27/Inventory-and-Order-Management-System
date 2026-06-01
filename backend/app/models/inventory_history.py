import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, gen_uuid


class InventoryChangeReason(str, enum.Enum):
    ORDER = "order"
    RESTOCK = "restock"
    ADJUSTMENT = "adjustment"
    ORDER_CANCELLED = "order_cancelled"


class InventoryHistory(Base):
    """Tracks every change to a product's stock level."""

    __tablename__ = "inventory_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=gen_uuid
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), index=True, nullable=False
    )
    change: Mapped[int] = mapped_column(nullable=False)  # +restock / -sale
    previous_quantity: Mapped[int] = mapped_column(nullable=False)
    new_quantity: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[InventoryChangeReason] = mapped_column(
        SAEnum(InventoryChangeReason, name="inventory_change_reason"), nullable=False
    )
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
