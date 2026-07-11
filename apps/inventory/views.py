from django.db import transaction
from rest_framework import viewsets

from core.permissions import IsInternOrAdmin

from .models import InventoryItem, InventoryLog
from .serializers import (
    InventoryItemSerializer,
    InventoryLogSerializer,
)


class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    queryset = (
        InventoryItem.objects.select_related("category")
        .all()
        .order_by("name")
    )
    permission_classes = [IsInternOrAdmin]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        old_item = self.get_object()
        old_quantity = old_item.quantity

        with transaction.atomic():
            item = serializer.save(updated_by=self.request.user)

            difference = item.quantity - old_quantity

            if difference != 0:
                InventoryLog.objects.create(
                    item=item,
                    change_type=(
                        InventoryLog.ChangeType.ADD
                        if difference > 0
                        else InventoryLog.ChangeType.REMOVE
                    ),
                    quantity_change=difference,
                    reason="Inventory updated",
                    performed_by=self.request.user,
                )

    def perform_destroy(self, instance):
        instance.delete()


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryLogSerializer
    queryset = (
        InventoryLog.objects.select_related(
            "item",
            "performed_by",
        )
        .all()
    )
    permission_classes = [IsInternOrAdmin]
