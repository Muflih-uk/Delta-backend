import mimetypes
import os
import uuid
from typing import BinaryIO

from django.core.files.uploadedfile import UploadedFile

from core.supabase import supabase


class StorageService:
    DEFAULT_BUCKET = "avatars"

    @staticmethod
    def _guess_content_type(filename: str) -> str:
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    @staticmethod
    def _generate_filename(filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        return f"{uuid.uuid4().hex}{ext}"

    @classmethod
    def upload_file(
        cls,
        bucket: str,
        folder: str,
        file: UploadedFile | BinaryIO,
        filename: str | None = None,
        upsert: bool = False,
    ) -> dict:

        if filename is None:
            filename = getattr(file, "name", "file")

        filename = cls._generate_filename(filename)

        path = f"{folder}/{filename}"

        content_type = cls._guess_content_type(filename)

        response = supabase.storage.from_(bucket).upload(
            path=path,
            file=file,
            file_options={
                "content-type": content_type,
                "upsert": str(upsert).lower(),
            },
        )

        public_url = supabase.storage.from_(bucket).get_public_url(path)

        return {
            "path": path,
            "url": public_url,
            "response": response,
        }

    @classmethod
    def upload_avatar(
        cls,
        user,
        image: UploadedFile,
    ) -> str:

        ext = os.path.splitext(image.name)[1]

        path = f"users/{user.id}/avatar{ext}"

        (
            supabase.storage.from_(cls.DEFAULT_BUCKET).upload(
                path,
                image,
                file_options={
                    "content-type": image.content_type,
                    "upsert": "true",
                },
            )
        )

        url = supabase.storage.from_(cls.DEFAULT_BUCKET).get_public_url(path)

        user.avatar_url = url
        user.save(update_fields=["avatar_url"])

        return url

    @staticmethod
    def delete_file(
        bucket: str,
        path: str,
    ) -> bool:

        (supabase.storage.from_(bucket).remove([path]))

        return True

    @classmethod
    def delete_avatar(cls, user):

        if not user.avatar_url:
            return

        ext = os.path.splitext(user.avatar_url)[1]

        path = f"users/{user.id}/avatar{ext}"

        cls.delete_file(
            cls.DEFAULT_BUCKET,
            path,
        )

        user.avatar_url = ""
        user.save(update_fields=["avatar_url"])

    @staticmethod
    def get_public_url(
        bucket: str,
        path: str,
    ) -> str:

        return supabase.storage.from_(bucket).get_public_url(path)

    @staticmethod
    def create_signed_url(
        bucket: str,
        path: str,
        expires_in: int = 3600,
    ) -> str:

        response = supabase.storage.from_(bucket).create_signed_url(
            path,
            expires_in,
        )

        return response["signedURL"]

    @staticmethod
    def list_files(
        bucket: str,
        folder: str = "",
    ):

        return supabase.storage.from_(bucket).list(folder)

    @classmethod
    def file_exists(
        cls,
        bucket: str,
        path: str,
    ) -> bool:

        folder = os.path.dirname(path)
        filename = os.path.basename(path)

        files = cls.list_files(
            bucket,
            folder,
        )

        return any(file["name"] == filename for file in files)
