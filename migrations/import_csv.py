#!/usr/bin/env python3
"""
CSV/Excel import script for ERP data migration.
Reads raw CSV/Excel files and loads them into Django models via the import pipeline.
"""
import csv
import sys
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

import django
import os

# Setup Django settings before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_migration.settings")
sys.path.insert(0, str(Path(__file__).parent.parent))
django.setup()

from migrations.models import (
    Customer, Vendor, Product, UnitOfMeasure,
    Order, OrderItem, PurchaseOrder,
    Invoice, GLEntry, InventoryMovement,
    ARLedgerEntry, APLedgerEntry,
)


class ImportError(Exception):
    """Row-level import error with line number and reason."""
    pass


def parse_date(val: str) -> date:
    """Parse date from common formats."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except (ValueError, AttributeError):
            pass
    raise ImportError(f"Unrecognized date format: {val!r}")


def parse_decimal(val: str) -> Decimal:
    """Parse decimal from currency/number strings."""
    if not val or val.strip() in ("", "NULL", "N/A", "None"):
        return Decimal("0.00")
    try:
        # Strip currency symbols and commas
        cleaned = val.strip().replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
        return Decimal(cleaned)
    except InvalidOperation:
        raise ImportError(f"Invalid decimal: {val!r}")


def load_customers(csv_path: Path) -> tuple[int, int, int]:
    """
    Load customers from CSV.
    Expected columns: customer_code, name, email, phone,
                      billing_address, shipping_address,
                      tax_id, payment_terms, credit_limit
    """
    created = updated = errors = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                defaults = {
                    "name": row["name"].strip(),
                    "email": row.get("email", "").strip(),
                    "phone": row.get("phone", "").strip(),
                    "billing_address": row.get("billing_address", "").strip(),
                    "shipping_address": row.get("shipping_address", "").strip(),
                    "tax_id": row.get("tax_id", "").strip(),
                    "payment_terms": row.get("payment_terms", "").strip(),
                    "credit_limit": parse_decimal(row.get("credit_limit", "0")),
                    "is_active": row.get("is_active", "true").strip().lower() != "false",
                }
                obj, was_created = Customer.objects.update_or_create(
                    customer_code=row["customer_code"].strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                print(f"  Line {lineno}: Customer {row.get('customer_code','?')} skipped — {e}")
    return created, updated, errors


def load_vendors(csv_path: Path) -> tuple[int, int, int]:
    """Load vendors from CSV. Expected columns: vendor_code, name, email, phone, address, tax_id, payment_terms."""
    created = updated = errors = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                defaults = {
                    "name": row["name"].strip(),
                    "email": row.get("email", "").strip(),
                    "phone": row.get("phone", "").strip(),
                    "address": row.get("address", "").strip(),
                    "tax_id": row.get("tax_id", "").strip(),
                    "payment_terms": row.get("payment_terms", "").strip(),
                    "is_active": row.get("is_active", "true").strip().lower() != "false",
                }
                obj, was_created = Vendor.objects.update_or_create(
                    vendor_code=row["vendor_code"].strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                print(f"  Line {lineno}: Vendor {row.get('vendor_code','?')} skipped — {e}")
    return created, updated, errors


def load_products(csv_path: Path) -> tuple[int, int, int]:
    """Load products from CSV. Requires: sku, name. Optional: description, category, unit_cost, unit_price."""
    created = updated = errors = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                uom = None
                if row.get("unit_of_measure"):
                    uom, _ = UnitOfMeasure.objects.get_or_create(
                        code=row["unit_of_measure"].strip(),
                        defaults={"name": row["unit_of_measure"].strip()},
                    )
                defaults = {
                    "name": row["name"].strip(),
                    "description": row.get("description", "").strip(),
                    "category": row.get("category", "").strip(),
                    "unit_of_measure": uom,
                    "unit_cost": parse_decimal(row.get("unit_cost", "0")),
                    "unit_price": parse_decimal(row.get("unit_price", "0")),
                    "reorder_point": parse_decimal(row.get("reorder_point", "0")),
                    "is_active": row.get("is_active", "true").strip().lower() != "false",
                }
                obj, was_created = Product.objects.update_or_create(
                    sku=row["sku"].strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                print(f"  Line {lineno}: Product {row.get('sku','?')} skipped — {e}")
    return created, updated, errors


def load_orders(csv_path: Path) -> tuple[int, int, int]:
    """Load orders from CSV. Requires: order_number, customer_code, order_date, status."""
    created = updated = errors = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            try:
                customer = Customer.objects.get(customer_code=row["customer_code"].strip())
                defaults = {
                    "order_date": parse_date(row["order_date"]),
                    "status": row.get("status", "draft").strip(),
                    "subtotal": parse_decimal(row.get("subtotal", "0")),
                    "tax_amount": parse_decimal(row.get("tax_amount", "0")),
                    "total_amount": parse_decimal(row.get("total_amount", "0")),
                    "notes": row.get("notes", "").strip(),
                }
                if row.get("shipped_date"):
                    defaults["shipped_date"] = parse_date(row["shipped_date"])
                obj, was_created = Order.objects.update_or_create(
                    order_number=row["order_number"].strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                print(f"  Line {lineno}: Order {row.get('order_number','?')} skipped — {e}")
    return created, updated, errors


def run_import(entity: str, csv_path: str, staging: bool = True) -> dict:
    """
    Run import for a given entity.
    Set staging=True to preview row counts without committing.
    Returns dict with created/updated/errors counts.
    """
    path = Path(csv_path)
    if not path.exists():
        return {"error": f"File not found: {csv_path}"}

    if staging:
        print(f"[STAGING MODE] Preview import: {entity} from {csv_path}")
        with open(path, newline="", encoding="utf-8") as f:
            row_count = sum(1 for _ in f) - 1  # subtract header
        print(f"  Rows in file: {row_count}")
        print(f"  Run with staging=False to actually import.")
        return {"staged": True, "rows": row_count}

    print(f"Importing {entity} from {csv_path} ...")

    if entity == "customers":
        created, updated, errors = load_customers(path)
    elif entity == "vendors":
        created, updated, errors = load_vendors(path)
    elif entity == "products":
        created, updated, errors = load_products(path)
    elif entity == "orders":
        created, updated, errors = load_orders(path)
    else:
        return {"error": f"Unknown entity: {entity}"}

    print(f"  Created: {created}, Updated: {updated}, Errors: {errors}")
    return {"created": created, "updated": updated, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ERP data import from CSV")
    parser.add_argument("entity", help="Entity to import (customers, vendors, products, orders)")
    parser.add_argument("csv_path", help="Path to CSV file")
    parser.add_argument("--live", action="store_true", help="Commit changes (default is staging preview)")
    args = parser.parse_args()

    result = run_import(args.entity, args.csv_path, staging=not args.live)
    print(result)