# ERP Data Migration - Django ORM Models
# Core domain models for ERP data import.
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class UnitOfMeasure(models.Model):
    """Units for products and inventory (each, case, lb, kg, etc.)."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "migrations_uom"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Customer(models.Model):
    """ERP customer entity with billing/shipping addresses."""
    customer_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=50, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_customer"
        ordering = ["customer_code"]

    def __str__(self):
        return f"{self.customer_code} — {self.name}"


class Vendor(models.Model):
    """ERP vendor/supplier entity."""
    vendor_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_vendor"
        ordering = ["vendor_code"]

    def __str__(self):
        return f"{self.vendor_code} — {self.name}"


class Product(models.Model):
    """ERP product/SKU entity with pricing and inventory data."""
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products"
    )
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0.00"))
    reorder_point = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_product"
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} — {self.name}"


class Order(models.Model):
    """ERP sales order header."""
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    order_date = models.DateField()
    shipped_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"), ("confirmed", "Confirmed"),
            ("shipped", "Shipped"), ("invoiced", "Invoiced"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_order"
        ordering = ["-order_date", "order_number"]

    def __str__(self):
        return f"{self.order_number} — {self.customer}"


class OrderItem(models.Model):
    """ERP sales order line item."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    warehouse_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "migrations_order_item"
        unique_together = [["order", "product"]]

    def save(self, *args, **kwargs):
        self.line_total = Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.order_number} — {self.product.sku} x {self.quantity}"


class PurchaseOrder(models.Model):
    """ERP purchase order header."""
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="purchase_orders")
    po_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"), ("issued", "Issued"),
            ("partial", "Partially Received"), ("received", "Received"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_purchase_order"
        ordering = ["-po_date", "po_number"]

    def __str__(self):
        return f"{self.po_number} — {self.vendor}"


class Invoice(models.Model):
    """ERP invoice (AR for sales, AP for purchases)."""
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, null=True, blank=True,
        related_name="ar_invoices"
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.PROTECT, null=True, blank=True,
        related_name="ap_invoices"
    )
    invoice_type = models.CharField(
        max_length=5,
        choices=[("AR", "Accounts Receivable"), ("AP", "Accounts Payable")],
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(
        max_length=20,
        choices=[
            ("open", "Open"), ("partial", "Partially Paid"),
            ("paid", "Paid"), ("overdue", "Overdue"),
            ("cancelled", "Cancelled"),
        ],
        default="open",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "migrations_invoice"
        ordering = ["-invoice_date", "invoice_number"]

    def __str__(self):
        return f"{self.invoice_number} ({self.invoice_type}) — {self.customer or self.vendor}"


class GLEntry(models.Model):
    """General Ledger journal entry."""
    gl_date = models.DateField()
    journal_code = models.CharField(max_length=20)
    document_number = models.CharField(max_length=50)
    account_code = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    description = models.TextField(blank=True)
    source = models.CharField(max_length=50, blank=True)  # e.g. "AR", "AP", "Inventory"
    source_id = models.CharField(max_length=50, blank=True)  # FK to source document
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "migrations_gl_entry"
        ordering = ["gl_date", "journal_code", "document_number"]
        indexes = [
            models.Index(fields=["gl_date"]),
            models.Index(fields=["account_code"]),
            models.Index(fields=["source", "source_id"]),
        ]

    def __str__(self):
        return f"{self.gl_date} {self.journal_code}/{self.document_number} {self.account_code}"


class InventoryMovement(models.Model):
    """Inventory movement ledger (receipts, issues, adjustments)."""
    movement_date = models.DateField()
    movement_type = models.CharField(
        max_length=20,
        choices=[
            ("receipt", "Receipt"), ("issue", "Issue"),
            ("adjustment", "Adjustment"), ("transfer", "Transfer"),
        ],
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    warehouse_code = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("0.00"))
    source_document = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "migrations_inventory_movement"
        ordering = ["-movement_date", "product__sku"]
        indexes = [models.Index(fields=["movement_date"]), models.Index(fields=["product"])]

    def __str__(self):
        return f"{self.movement_date} {self.movement_type} {self.product.sku} {self.quantity}"


class ARLedgerEntry(models.Model):
    """Accounts Receivable sub-ledger entry."""
    entry_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="ar_entries")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True,
                                related_name="ar_entries")
    transaction_type = models.CharField(
        max_length=20,
        choices=[("invoice", "Invoice"), ("payment", "Payment"), ("credit", "Credit Memo"), ("adjustment", "Adjustment")],
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "migrations_ar_ledger"
        ordering = ["-entry_date", "customer"]
        indexes = [models.Index(fields=["entry_date"]), models.Index(fields=["customer"])]

    def __str__(self):
        return f"{self.entry_date} {self.customer} {self.transaction_type} {self.amount}"


class APLedgerEntry(models.Model):
    """Accounts Payable sub-ledger entry."""
    entry_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="ap_entries")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True,
                                related_name="ap_entries")
    transaction_type = models.CharField(
        max_length=20,
        choices=[("invoice", "Invoice"), ("payment", "Payment"), ("credit", "Credit Memo"), ("adjustment", "Adjustment")],
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "migrations_ap_ledger"
        ordering = ["-entry_date", "vendor"]
        indexes = [models.Index(fields=["entry_date"]), models.Index(fields=["vendor"])]

    def __str__(self):
        return f"{self.entry_date} {self.vendor} {self.transaction_type} {self.amount}"