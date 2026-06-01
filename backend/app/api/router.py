from fastapi import APIRouter

from app.api.routes import auth, customers, dashboard, orders, products

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(customers.router)
api_router.include_router(orders.router)
api_router.include_router(dashboard.router)
