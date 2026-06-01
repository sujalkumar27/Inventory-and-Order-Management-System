# Database Design

UUID primary keys are used across all tables. Timestamps are timezone-aware.
Products, customers, orders and users support **soft delete** via `is_deleted` /
`deleted_at`.

## ER Diagram

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "is referenced by"
    PRODUCTS ||--o{ INVENTORY_HISTORY : "tracks"

    USERS {
        uuid id PK
        string full_name
        string email UK
        string hashed_password
        enum role "admin | user"
        bool is_active
        bool is_deleted
        timestamp created_at
        timestamp updated_at
    }

    PRODUCTS {
        uuid id PK
        string sku UK
        string name
        text description
        numeric price "CHECK >= 0"
        int stock_quantity "CHECK >= 0"
        bool is_deleted
        timestamp created_at
        timestamp updated_at
    }

    CUSTOMERS {
        uuid id PK
        string first_name
        string last_name
        string email UK
        string phone
        text address
        bool is_deleted
        timestamp created_at
        timestamp updated_at
    }

    ORDERS {
        uuid id PK
        uuid customer_id FK
        timestamp order_date
        numeric total_amount
        enum status "pending | processing | completed | cancelled"
        bool is_deleted
        timestamp created_at
        timestamp updated_at
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity "CHECK > 0"
        numeric unit_price "CHECK >= 0"
    }

    INVENTORY_HISTORY {
        uuid id PK
        uuid product_id FK
        int change
        int previous_quantity
        int new_quantity
        enum reason "order | restock | adjustment | order_cancelled"
        uuid reference_id
        timestamp created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        string entity_id
        text detail
        timestamp created_at
    }
```

## Relationships

- One **Customer** → many **Orders**
- One **Order** → many **Order Items**
- One **Product** → many **Order Items**
- One **Product** → many **Inventory History** entries
- One **User** → many **Audit Logs**

## Constraints

| Table        | Constraint                                  |
| ------------ | ------------------------------------------- |
| products     | `sku` unique; `price >= 0`; `stock >= 0`    |
| customers    | `email` unique                              |
| users        | `email` unique                              |
| order_items  | `quantity > 0`; `unit_price >= 0`           |

Migrations are managed by Alembic (`backend/alembic/versions/0001_initial_schema.py`).
