from rest_framework import serializers

from .models import InventoryItem, InventoryLog


class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "name",
            "category",
            "category_name",
            "description",
            "quantity",
            "unit",
            "low_stock_threshold",
            "location",
            "image_url",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_low_stock",
        ]


class InventoryLogSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    performed_by_name = serializers.CharField(
        source="performed_by.full_name",
        read_only=True,
    )

    class Meta:
        model = InventoryLog
        fields = [
            "id",
            "item",
            "item_name",
            "change_type",
            "quantity_change",
            "reason",
            "performed_by",
            "performed_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "performed_by",
            "created_at",
        ]
