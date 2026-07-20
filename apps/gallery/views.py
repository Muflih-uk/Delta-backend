from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsInternOrAdmin
from core.storage import StorageService

from .models import GalleryAlbum, GalleryImage
from .serializers import (
    GalleryAlbumListSerializer,
    GalleryAlbumSerializer,
    GalleryImageSerializer,
)

GALLERY_BUCKET = "gallery"


class GalleryAlbumViewSet(viewsets.ModelViewSet):
    """
    CRUD for gallery albums.

    - list / retrieve  → public (anyone)
    - create / update / delete → intern or admin only

    GET    /api/gallery/albums/          → list all published albums (public)
    GET    /api/gallery/albums/{id}/     → retrieve album with images (public)
    POST   /api/gallery/albums/          → create album (intern/admin)
    PUT    /api/gallery/albums/{id}/     → update album (intern/admin)
    PATCH  /api/gallery/albums/{id}/     → partial update (intern/admin)
    DELETE /api/gallery/albums/{id}/     → delete album + all images (intern/admin)
    """

    def get_queryset(self):
        user = self.request.user
        if self.action in ["list", "retrieve"] and not (
            user.is_authenticated
            and getattr(user, "role", None) in ["intern", "admin"]
        ):
            # Public: only published albums
            return GalleryAlbum.objects.prefetch_related("images").filter(is_published=True)
        return GalleryAlbum.objects.prefetch_related("images").all()

    def get_serializer_class(self):
        if self.action == "list":
            return GalleryAlbumListSerializer
        return GalleryAlbumSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsInternOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        album = self.get_object()
        # Delete all images from Supabase storage before removing DB records
        for image in album.images.all():
            if image.storage_path:
                try:
                    StorageService.delete_file(GALLERY_BUCKET, image.storage_path)
                except Exception:
                    pass  # Log but don't block deletion
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GalleryImageViewSet(viewsets.ModelViewSet):
    """
    CRUD for individual gallery images.

    - list / retrieve  → public
    - create / update / delete → intern or admin only

    POST /api/gallery/images/upload/  → upload image file (multipart, intern/admin)

    GET    /api/gallery/images/          → list all images
    GET    /api/gallery/images/{id}/     → retrieve image
    POST   /api/gallery/images/          → create image record (without file upload)
    PUT    /api/gallery/images/{id}/     → update metadata
    PATCH  /api/gallery/images/{id}/     → partial update
    DELETE /api/gallery/images/{id}/     → delete image + remove from Supabase
    POST   /api/gallery/images/upload/   → upload image file → returns image record
    """

    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        qs = GalleryImage.objects.select_related("album", "uploaded_by")
        album_id = self.request.query_params.get("album")
        if album_id:
            qs = qs.filter(album_id=album_id)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsInternOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        image = self.get_object()
        if image.storage_path:
            try:
                StorageService.delete_file(GALLERY_BUCKET, image.storage_path)
            except Exception:
                pass
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
        url_path="upload",
        permission_classes=[IsAuthenticated, IsInternOrAdmin],
        parser_classes=[MultiPartParser],
    )
    def upload(self, request):
        """
        Upload an image file to Supabase Storage and create a GalleryImage record.

        Form fields:
            image   (file)    — required
            album   (uuid)    — required
            title   (str)     — optional
            caption (str)     — optional
        """
        image_file = request.FILES.get("image")
        album_id = request.data.get("album")

        if not image_file:
            return Response(
                {"success": False, "message": "image file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not album_id:
            return Response(
                {"success": False, "message": "album id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            album = GalleryAlbum.objects.get(id=album_id)
        except GalleryAlbum.DoesNotExist:
            return Response(
                {"success": False, "message": "Album not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = StorageService.upload_file(
                bucket=GALLERY_BUCKET,
                folder=f"albums/{album.id}",
                file=image_file,
                filename=image_file.name,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Upload failed: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        gallery_image = GalleryImage.objects.create(
            album=album,
            title=request.data.get("title", ""),
            caption=request.data.get("caption", ""),
            image_url=result["url"],
            storage_path=result["path"],
            uploaded_by=request.user,
        )

        serializer = GalleryImageSerializer(gallery_image)

        return Response(
            {"success": True, "image": serializer.data},
            status=status.HTTP_201_CREATED,
        )
