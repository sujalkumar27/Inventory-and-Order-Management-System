# API Documentation

Base URL: `http://localhost:8000/api`
Interactive docs (Swagger UI): `http://localhost:8000/docs`
OpenAPI schema: `http://localhost:8000/openapi.json`

All endpoints except `/auth/register`, `/auth/login` and `/auth/refresh` require a
`Authorization: Bearer <access_token>` header.

## Error envelope

Errors return a consistent shape:

```json
{ "success": false, "message": "SKU already exists" }
```

Validation errors additionally include an `errors` array:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [{ "field": "price", "message": "Input should be greater than or equal to 0" }]
}
```

## Authentication

| Method | Path                  | Body                                   | Notes                       |
| ------ | --------------------- | -------------------------------------- | --------------------------- |
| POST   | `/auth/register`      | `full_name, email, password (>=8)`     | Returns the created user    |
| POST   | `/auth/login`         | `email, password`                      | Returns access + refresh    |
| POST   | `/auth/refresh`       | `refresh_token`                        | Returns a new token pair    |
| GET    | `/auth/me`            | —                                      | Current user                |

## Products

| Method | Path              | Notes                                                                    |
| ------ | ----------------- | ------------------------------------------------------------------------ |
| GET    | `/products`       | Query: `page, page_size, search, sort_by(name\|price\|stock_quantity), order(asc\|desc), in_stock(bool)` |
| GET    | `/products/{id}`  | Single product                                                           |
| POST   | `/products`       | `sku, name, description, price, stock_quantity`                          |
| PUT    | `/products/{id}`  | Partial update                                                           |
| DELETE | `/products/{id}`  | Soft delete                                                              |

## Customers

| Method | Path               | Notes                                            |
| ------ | ------------------ | ------------------------------------------------ |
| GET    | `/customers`       | Query: `page, page_size, search`                 |
| GET    | `/customers/{id}`  | Single customer                                  |
| POST   | `/customers`       | `first_name, last_name, email, phone, address`   |
| PUT    | `/customers/{id}`  | Partial update                                   |
| DELETE | `/customers/{id}`  | Soft delete                                      |

## Orders

| Method | Path             | Notes                                                       |
| ------ | ---------------- | ----------------------------------------------------------- |
| GET    | `/orders`        | Query: `page, page_size, status, customer_id`               |
| GET    | `/orders/{id}`   | Order with items                                            |
| POST   | `/orders`        | `customer_id, items:[{product_id, quantity}]`               |
| PUT    | `/orders/{id}`   | `status` — cancelling restores stock                        |
| DELETE | `/orders/{id}`   | Soft delete; restores stock if not cancelled                |

### Order creation logic

1. Validate the customer exists.
2. Validate every product exists.
3. Validate each quantity (> 0).
4. Check stock availability per product.
5. If any product has insufficient stock → `400 { "success": false, "message": "Insufficient inventory" }` and **no order is created**.
6. Otherwise create the order + items, deduct stock, and write inventory history.
7. `total_amount` is computed automatically from `unit_price * quantity`.

## Dashboard

| Method | Path                          | Notes                                                  |
| ------ | ----------------------------- | ------------------------------------------------------ |
| GET    | `/dashboard/stats`            | Stat cards + monthly orders, revenue, top/low products |
| GET    | `/dashboard/products/export`  | CSV export of products                                 |
