from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InventoryCategoryViewSet, InventoryItemViewSet, InventoryLogViewSet

router = DefaultRouter()

router.register(
    "inventory-categories",
    InventoryCategoryViewSet,
    basename="inventory-categories",
)

router.register(
    "inventory",
    InventoryItemViewSet,
    basename="inventory",
)

router.register(
    "inventory-logs",
    InventoryLogViewSet,
    basename="inventory-logs",
)

urlpatterns = [
    path("", include(router.urls)),
]
