from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GalleryAlbumViewSet, GalleryImageViewSet

router = DefaultRouter()

router.register(
    "albums",
    GalleryAlbumViewSet,
    basename="gallery-albums",
)

router.register(
    "images",
    GalleryImageViewSet,
    basename="gallery-images",
)

urlpatterns = [
    path("", include(router.urls)),
]
