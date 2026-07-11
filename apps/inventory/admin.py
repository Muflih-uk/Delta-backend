from django.contrib import admin

from .models import (
    InventoryCategory,
    InventoryItem,
    InventoryLog,
)


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name","id")
    search_fields = ("name",)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "quantity",
        "unit",
        "is_low_stock",
        "location",
    )
    list_filter = (
        "category",
    )
    search_fields = (
        "name",
        "description",
        "location",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "change_type",
        "quantity_change",
        "performed_by",
        "created_at",
    )
    list_filter = (
        "change_type",
        "created_at",
    )
    search_fields = (
        "item__name",
        "reason",
    )
    readonly_fields = (
        "created_at",
    )
