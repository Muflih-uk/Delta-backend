from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "avatar_url",
            "created_at",
        )

        read_only_fields = (
            "id",
            "created_at",
        )


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    phone = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    role = serializers.ChoiceField(
        choices=User.Role.choices,
        default=User.Role.STUDENT,
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
    )


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "phone",
            "avatar_url",
        )
