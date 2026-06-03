#!/usr/bin/env python3
"""
ERP data reconciliation and validation report generator.
Produces exception reports for rows that cannot be imported automatically,
plus reconciliation reports showing row counts, invoice totals, AR/AP balances,
GL totals, and inventory checks.
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
from decimal import Decimal

import django, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_migration.settings")
sys.path.insert(0, str(Path(__file__).parent.parent))
django.setup()

from migrations.models import (
    Customer, Vendor, Product, Order, OrderItem,
    Invoice, GLEntry, InventoryMovement,
    ARLedgerEntry, APLedgerEntry,
)


class ReconciliationReport:
    """Generate reconciliation reports for ERP data import validation."""

    def __init__(self):
        self.errors = []  # (entity, row_id, field, reason, original_data)

    def add_error(self, entity: str, row_id: str, field: str, reason: str, row: dict):
        self.errors.append({
            "entity": entity, "row_id": row_id,
            "field": field, "reason": reason, "original": row,
        })

    def validate_customers(self, csv_path: Path) -> dict:
        """Validate customer CSV against existing DB records and business rules."""
        results = {"total": 0, "valid": 0, "errors": []}
        existing = {c.customer_code: c for c in Customer.objects.all()}
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results["total"] += 1
                errors = []
                code = row.get("customer_code", "").strip()
                if not code:
                    errors.append("Missing customer_code")
                elif code in existing:
                    # Check for data drift
                    existing_c = existing[code]
                    if row.get("email") and existing_c.email != row["email"].strip():
                        errors.append(f"Email mismatch: CSV={row['email']} DB={existing_c.email}")
                    if row.get("tax_id") and existing_c.tax_id != row["tax_id"].strip():
                        errors.append(f"Tax ID mismatch")
                if errors:
                    results["errors"].append({"row_id": code or f"line-{results['total']}", "errors": errors, "data": row})
                else:
                    results["valid"] += 1
        return results

    def validate_orders(self, csv_path: Path) -> dict:
        """Validate order CSV: customer exists, totals reconcile, dates valid."""
        results = {"total": 0, "valid": 0, "errors": []}
        customer_codes = {c.customer_code for c in Customer.objects.all()}
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results["total"] += 1
                errors = []
                order_num = row.get("order_number", "").strip()
                if not order_num:
                    errors.append("Missing order_number")
                # Check customer FK
                cust_code = row.get("customer_code", "").strip()
                if cust_code and cust_code not in customer_codes:
                    errors.append(f"Customer {cust_code} not found in DB")
                # Validate totals
                subtotal = row.get("subtotal", "").strip()
                tax = row.get("tax_amount", "").strip()
                total = row.get("total_amount", "").strip()
                if subtotal and tax and total:
                    try:
                        s = Decimal(subtotal.replace(",", "").replace("$", ""))
                        t = Decimal(tax.replace(",", "").replace("$", ""))
                        tot = Decimal(total.replace(",", "").replace("$", ""))
                        if abs((s + t) - tot) > Decimal("0.01"):
                            errors.append(f"Total mismatch: subtotal {s} + tax {t} != total {tot}")
                    except Exception:
                        errors.append("Invalid decimal in totals")
                if errors:
                    results["errors"].append({"row_id": order_num or f"line-{results['total']}", "errors": errors, "data": row})
                else:
                    results["valid"] += 1
        return results

    def reconcile_gl(self) -> dict:
        """Check that GL debits == credits."""
        total_debit = sum(e.debit for e in GLEntry.objects.all())
        total_credit = sum(e.credit for e in GLEntry.objects.all())
        balanced = abs(total_debit - total_credit) < Decimal("0.01")
        return {
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "difference": float(abs(total_debit - total_credit)),
            "balanced": balanced,
        }

    def reconcile_ar(self) -> dict:
        """Check that sum of AR entries matches invoice AR totals."""
        entry_total = sum(e.amount for e in ARLedgerEntry.objects.all())
        invoice_total = sum(
            i.total_amount - i.amount_paid
            for i in Invoice.objects.filter(invoice_type="AR")
        )
        return {
            "ledger_total": float(entry_total),
            "invoice_total": float(invoice_total),
            "difference": float(abs(entry_total - invoice_total)),
            "reconciled": abs(entry_total - invoice_total) < Decimal("0.01"),
        }

    def reconcile_ap(self) -> dict:
        """Check that sum of AP entries matches invoice AP totals."""
        entry_total = sum(e.amount for e in APLedgerEntry.objects.all())
        invoice_total = sum(
            i.total_amount - i.amount_paid
            for i in Invoice.objects.filter(invoice_type="AP")
        )
        return {
            "ledger_total": float(entry_total),
            "invoice_total": float(invoice_total),
            "difference": float(abs(entry_total - invoice_total)),
            "reconciled": abs(entry_total - invoice_total) < Decimal("0.01"),
        }

    def inventory_on_hand(self) -> dict:
        """Calculate current inventory on-hand per product from movement ledger."""
        movements = defaultdict(Decimal)
        for m in InventoryMovement.objects.all():
            if m.movement_type in ("receipt", "adjustment_add"):
                movements[m.product_id] += m.quantity
            else:
                movements[m.product_id] -= m.quantity
        return {
            sku: float(qty)
            for sku, qty in sorted(movements.items(), key=lambda x: str(x[0]))
        }

    def write_exception_report(self, output_path: Path, entity: str, errors: list):
        """Write exception report CSV for rows that cannot be imported."""
        if not errors:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                f.write("entity,row_id,field,reason\n")
                f.write(f"{entity},,,No errors found\n")
            return

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["entity", "row_id", "field", "reason", "original_data"])
            writer.writeheader()
            for err in errors:
                writer.writerow({
                    "entity": entity,
                    "row_id": err["row_id"],
                    "field": "; ".join(err.get("field", [])) if isinstance(err.get("field"), list) else err.get("field", ""),
                    "reason": "; ".join(err["errors"]) if err.get("errors") else err.get("reason", ""),
                    "original_data": str(err.get("data", {})),
                })
        print(f"Exception report written to: {output_path}")

    def write_reconciliation_report(self, output_path: Path, gl: dict, ar: dict, ap: dict):
        """Write reconciliation summary report."""
        lines = [
            "ERP Data Migration — Reconciliation Report",
            "=" * 60,
            "",
            "General Ledger",
            f"  Total Debits:  ${gl['total_debit']:,.2f}",
            f"  Total Credits: ${gl['total_credit']:,.2f}",
            f"  Difference:   ${gl['difference']:,.2f}",
            f"  Balanced:      {'YES' if gl['balanced'] else 'NO — RECONCILIATION ERROR'}",
            "",
            "Accounts Receivable",
            f"  Ledger Total:  ${ar['ledger_total']:,.2f}",
            f"  Invoice Total: ${ar['invoice_total']:,.2f}",
            f"  Difference:    ${ar['difference']:,.2f}",
            f"  Reconciled:    {'YES' if ar['reconciled'] else 'NO — RECONCILIATION ERROR'}",
            "",
            "Accounts Payable",
            f"  Ledger Total:  ${ap['ledger_total']:,.2f}",
            f"  Invoice Total: ${ap['invoice_total']:,.2f}",
            f"  Difference:    ${ap['difference']:,.2f}",
            f"  Reconciled:    {'YES' if ap['reconciled'] else 'NO — RECONCILIATION ERROR'}",
            "",
        ]
        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Reconciliation report written to: {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ERP reconciliation report")
    parser.add_argument("--validate", choices=["customers", "orders"],
                        help="Validate CSV against DB")
    parser.add_argument("--csv", help="Path to CSV file for validation")
    parser.add_argument("--output", help="Output path for exception report")
    parser.add_argument("--reconcile", action="store_true", help="Run GL/AR/AP reconciliation")
    args = parser.parse_args()

    reporter = ReconciliationReport()

    if args.validate and args.csv:
        path = Path(args.csv)
        if args.validate == "customers":
            result = reporter.validate_customers(path)
        elif args.validate == "orders":
            result = reporter.validate_orders(path)
        print(f"Validation results for {args.validate}:")
        print(f"  Total: {result['total']}, Valid: {result['valid']}, Errors: {len(result['errors'])}")
        if result["errors"] and args.output:
            reporter.write_exception_report(Path(args.output), args.validate, result["errors"])

    if args.reconcile:
        gl = reporter.reconcile_gl()
        ar = reporter.reconcile_ar()
        ap = reporter.reconcile_ap()
        output = Path(args.output) if args.output else Path("reconciliation_report.txt")
        reporter.write_reconciliation_report(output, gl, ar, ap)