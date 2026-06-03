# ERP Data Migration Engineer

Production-ready project — see SPEC.md for full documentation.

## Business Problem Solved

This platform needed a data migration engineer who could safely transfer legacy ERP data (customers, products, orders, accounting, inventory, AR/AP, GL, purchase orders) from CSV/Excel/exports into a Django/PostgreSQL backend — with proper validation, exception reporting, and reconciliation before production cutover. The resulting engineer builds idempotent migration scripts, handles messy business data edge cases, and produces clean GitHub PRs with full documentation.

## Technical Stack

Python · Django · Django ORM · PostgreSQL · SQL · pandas · NumPy · ETL · CSV/Excel parsing · AWS/RDS · Docker · pytest · Git · PR/Merge Review · ERP domain (AR/AP, GL, Inventory Management, Order Processing) · Idempotent Scripts · Data Reconciliation

## Architecture

The system uses a Django ORM layer over PostgreSQL with a migration framework that:
1. Reads raw CSV/Excel/ERP export files
2. Transforms and validates data via pandas
3. Loads into staging tables via Django bulk operations
4. Reconciles against source totals before final commit
5. Produces exception reports for manual review

## Data Model

Core entities: Customer, Vendor, Product, UnitOfMeasure, Order, OrderItem, PurchaseOrder, Invoice, CreditOrder, AREntry, APEntry, GLEntry, InventoryMovement, Payment.
All entities use UUID primary keys with created_at/updated_at timestamps and soft-delete support. Relationships use foreign key constraints with ON DELETE CASCADE.

## Project Structure

```
erp-data-migration/
├── migrations/          # Django migration scripts (customers, products, orders, accounting, inventory)
├── validators/          # Reconciliation & exception reporting
├── scripts/             # Standalone ETL utilities
├── tests/              # pytest-based validation suite
├── docs/               # Migration runbooks
├── Dockerfile
└── docker-compose.yml
```

## Scope

**In Scope:**
- Django ORM models for all ERP entities (AR/AP, GL, inventory, orders)
- CSV/Excel import scripts with pandas
- Validation & reconciliation reports
- Exception handling & error reporting
- Staging/production migration safety
- GitHub PR workflow with documentation

**Out of Scope:**
- Frontend UI (no React/dashboard)
- Real-time API endpoints (beyond admin)
- Production deployment (staging only)
- Data entry work (scripts only)

## Quality Requirements

- All migration scripts must be idempotent (safely rerunnable)
- Row counts, invoice totals, AR/AP balances must reconcile before production cutover
- Every exception row must produce a readable error report
- All code via GitHub PR with review notes