# ERP Data Migration Engineer

**Lead:** https://www.upwork.com/jobs/~022061935007481320302
**Client:** ERP Data Migration Client
**Tier:** MICRO | **Budget:** $35-$50/hr | **Duration:** 1-3 months (contract-to-hire)

---

## 🎯 Business Problem Solved

This platform needed a data migration engineer who could safely transfer legacy ERP data (customers, products, orders, accounting, inventory, AR/AP, GL, purchase orders) from CSV/Excel/exports into a Django/PostgreSQL backend — with proper validation, exception reporting, and reconciliation before production cutover. The resulting engineer builds idempotent migration scripts, handles messy business data edge cases, and produces clean GitHub PRs with full documentation.

---

## Technical Stack

- **Backend:** Python, Django, Django ORM, PostgreSQL
- **Data Processing:** pandas, NumPy, CSV/Excel parsing
- **ETL:** SQL-based transforms, batch processing, staging tables
- **Infrastructure:** AWS/RDS, Docker, pytest
- **Workflow:** Git, GitHub Pull Requests, code review
- **Domain:** ERP (AR/AP, GL, Inventory Management, Order Processing)

## Architecture

The system uses a Django ORM layer over PostgreSQL with a migration framework that:
1. Reads raw CSV/Excel/ERP export files
2. Transforms and validates data via pandas
3. Loads into staging tables via Django bulk operations
4. Reconciles against source totals before final commit
5. Produces exception reports for manual review

## Data Model

Core entities: Customer, Vendor, Product, UnitOfMeasure, Order, OrderItem, PurchaseOrder, Invoice, CreditOrder, AREntry, APEntry, GLEntry, InventoryMovement, Payment.

## Repository Structure

```
erp-data-migration/
├── SPEC.md              ← This specification
├── README.md            ← You are here
├── migrations/          ← Django migration scripts
│   ├── customers/
│   ├── products/
│   ├── orders/
│   ├── accounting/      ← AR/AP, GL entries
│   └── inventory/
├── validators/          ← Reconciliation & exception reporting
├── scripts/             ← Standalone ETL utilities
├── tests/               ← pytest-based validation suite
└── docs/                ← Migration runbooks
```

## Scope

**In Scope:**
- Django ORM models for all ERP entities
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
- Row counts, invoice totals, AR/AP balances must reconcile before production
- Every exception row must produce a readable error report
- All code via GitHub PR with review notes

## Contact

Apply at: https://www.upwork.com/jobs/~022061935007481320302