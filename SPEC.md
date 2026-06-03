# Specification: Data migration engineer for ERP: migrate legacy customer, product, order, accounting, inventory, AR/AP, GL, purchase order data into Django/PostgreSQL. Clean CSV/Excel/ERP exports, write Python/Django import scripts, pandas + Django ORM, exception reports, validation/reconciliation reports, GitHub PR workflow. Strong Python/PostgreSQL/Django ORM required. ERP experience strongly preferred. $35-50/hr, 1-3 months, contract-to-hire.

## 1. Project Overview

**Project:** Data migration engineer for ERP: migrate legacy customer, product, order, accounting, inventory, AR/AP, GL, purchase order data into Django/PostgreSQL. Clean CSV/Excel/ERP exports, write Python/Django import scripts, pandas + Django ORM, exception reports, validation/reconciliation reports, GitHub PR workflow. Strong Python/PostgreSQL/Django ORM required. ERP experience strongly preferred. $35-50/hr, 1-3 months, contract-to-hire.
**GitHub:** https://github.com/9KMan/JOB-20260603035153-000066
**Lead:** 5-0/hr
**Client:** ERP Data Migration Client
**Tier:** MICRO
**Budget:** $35-$50/hr
**Rate:** None

## 2. Technical Stack

Python · Django · PostgreSQL · SQL · pandas · Django ORM · ETL · ETL Pipeline · CSV · Excel · Celery · AWS · RDS · Docker · pytest · Git · PR/Merge Review · ERP · AR/AP · GL · Inventory Management · Food Distribution · Wholesale · Warehouse Logistics · Idempotent Scripts · Data Reconciliation

## 3. Architecture

- Backend: Python (FastAPI/Flask) REST API
- Database: PostgreSQL with proper indexing

### API Design
- RESTful endpoints with JSON request/response
- Authentication via JWT (HS256) or bcrypt
- Middleware for logging, error handling, CORS
- Versioned routes (/api/v1/...)

### Data Layer
- PostgreSQL as primary datastore
- Connection pooling via PGBouncer or similar
- Migration management via Alembic or raw SQL
- Indexes on foreign keys and high-cardinality columns

### Frontend (if applicable)
- Single-page application or server-rendered pages
- Responsive UI with modern CSS/JS framework
- State management for complex client-side logic

## 4. Data Model

### Core Entities
- Define entity schema based on job requirements
- Use UUIDs for primary keys (not auto-increment)
- Add created_at / updated_at timestamps to all tables
- Soft-delete pattern where appropriate

### Relationships
- Foreign key constraints with ON DELETE CASCADE
- Many-to-many via junction tables
- Eager loading for nested relationships in API

## 5. Project Structure

```
├── api/                  # FastAPI / Express routes + schemas
├── models/               # DB models / SQLAlchemy / Prisma
├── services/             # Business logic layer
├── workers/              # Background jobs (Celery, BullMQ, etc.)
├── migrations/           # DB migrations (Alembic / Flyway)
├── tests/                # Unit + integration tests
├── Dockerfile            # Production container
├── docker-compose.yml     # Local dev environment
└── README.md             # Setup instructions
```

## 6. Out of Scope

- Mobile apps (web only unless specified)
- Third-party integrations not mentioned in requirements
- Performance optimization at scale (1M+ users)
- White-label / multi-tenant unless explicitly required

## 7. Acceptance Criteria

- [ ] Database schema created and migrations applied
- [ ] Frontend UI implemented and responsive

**GitHub:** https://github.com/9KMan/JOB-20260603035153-000066
