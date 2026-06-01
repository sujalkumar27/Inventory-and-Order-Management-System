from decimal import Decimal

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    total_revenue: Decimal


class MonthlyOrders(BaseModel):
    month: str  # YYYY-MM
    orders: int
    revenue: Decimal


class TopProduct(BaseModel):
    product_id: str
    name: str
    units_sold: int
    revenue: Decimal


class LowStockProduct(BaseModel):
    product_id: str
    sku: str
    name: str
    stock_quantity: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    monthly_orders: list[MonthlyOrders]
    top_products: list[TopProduct]
    low_stock: list[LowStockProduct]
