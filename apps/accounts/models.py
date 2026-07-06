import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        INTERN = "intern", "Intern"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    supabase_uid = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    avatar_url = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "users"

        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_intern(self):
        return self.role == self.Role.INTERN

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
