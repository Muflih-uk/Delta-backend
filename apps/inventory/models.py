import uuid

from django.conf import settings
from django.db import models


class InventoryCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "inventory_categories"
        verbose_name_plural = "Inventory categories"

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        InventoryCategory, on_delete=models.PROTECT, related_name="items"
    )
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default="pcs")
    low_stock_threshold = models.PositiveIntegerField(default=5)
    location = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory_items"
        ordering = ["name"]
        indexes = [models.Index(fields=["category"])]

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.low_stock_threshold


class InventoryLog(models.Model):
    """Audit trail for every quantity change — add / remove / adjustment."""

    class ChangeType(models.TextChoices):
        ADD = "add", "Add"
        REMOVE = "remove", "Remove"
        ADJUSTMENT = "adjustment", "Adjustment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="logs"
    )
    change_type = models.CharField(max_length=10, choices=ChangeType.choices)
    quantity_change = models.IntegerField(help_text="Positive or negative delta")
    reason = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["item", "-created_at"])]

    def __str__(self):
        return f"{self.item.name} {self.change_type} {self.quantity_change:+d}"
