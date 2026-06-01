from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardStats,
    LowStockProduct,
    MonthlyOrders,
    TopProduct,
)

LOW_STOCK_THRESHOLD = 10
REVENUE_STATUSES = (OrderStatus.COMPLETED, OrderStatus.PROCESSING, OrderStatus.PENDING)


def get_dashboard(db: Session) -> DashboardResponse:
    total_products = db.scalar(
        select(func.count()).select_from(Product).where(Product.is_deleted.is_(False))
    ) or 0
    total_customers = db.scalar(
        select(func.count()).select_from(Customer).where(Customer.is_deleted.is_(False))
    ) or 0
    total_orders = db.scalar(
        select(func.count()).select_from(Order).where(Order.is_deleted.is_(False))
    ) or 0
    total_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.total_amount), 0)).where(
            Order.is_deleted.is_(False), Order.status.in_(REVENUE_STATUSES)
        )
    ) or Decimal("0")

    stats = DashboardStats(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        total_revenue=Decimal(total_revenue),
    )

    # Monthly orders + revenue (last 12 months bucket).
    month = func.to_char(Order.order_date, "YYYY-MM")
    monthly_rows = db.execute(
        select(month.label("m"), func.count(Order.id), func.coalesce(func.sum(Order.total_amount), 0))
        .where(Order.is_deleted.is_(False))
        .group_by("m")
        .order_by("m")
    ).all()
    monthly = [
        MonthlyOrders(month=r[0], orders=r[1], revenue=Decimal(r[2])) for r in monthly_rows
    ]

    # Top selling products by units sold.
    top_rows = db.execute(
        select(
            Product.id, Product.name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("units"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("rev"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.is_deleted.is_(False))
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    ).all()
    top_products = [
        TopProduct(product_id=str(r[0]), name=r[1], units_sold=int(r[2]), revenue=Decimal(r[3]))
        for r in top_rows
    ]

    low_rows = db.scalars(
        select(Product)
        .where(Product.is_deleted.is_(False), Product.stock_quantity <= LOW_STOCK_THRESHOLD)
        .order_by(Product.stock_quantity.asc())
        .limit(10)
    ).all()
    low_stock = [
        LowStockProduct(product_id=str(p.id), sku=p.sku, name=p.name,
                        stock_quantity=p.stock_quantity)
        for p in low_rows
    ]

    return DashboardResponse(
        stats=stats, monthly_orders=monthly, top_products=top_products, low_stock=low_stock
    )
