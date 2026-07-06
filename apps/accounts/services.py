from django.db import transaction

from core.supabase import supabase

from .models import User


class AccountService:
    @staticmethod
    @transaction.atomic
    def register(data):

        response = supabase.auth.sign_up(
            {
                "email": data["email"],
                "password": data["password"],
            }
        )

        if response.user is None:
            raise Exception("Supabase signup failed")

        user = User.objects.create(
            supabase_uid=response.user.id,
            username=data["username"],
            email=data["email"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
            role=data.get(
                "role",
                User.Role.STUDENT,
            ),
        )

        return {
            "user": user,
            "session": response.session,
        }

    @staticmethod
    def login(email, password):

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        if response.user is None:
            raise Exception("Invalid credentials")

        user = User.objects.get(supabase_uid=response.user.id)

        return {
            "user": user,
            "session": response.session,
        }

    @staticmethod
    def profile(user):

        return user

    @staticmethod
    def update_profile(user, serializer):

        serializer.save()

        return serializer.instance

    @staticmethod
    def delete(user):

        user.delete()

    @staticmethod
    def get_user(supabase_uid):

        return User.objects.get(supabase_uid=supabase_uid)

    @staticmethod
    def students():

        return User.objects.filter(role=User.Role.STUDENT)

    @staticmethod
    def interns():

        return User.objects.filter(role=User.Role.INTERN)

    @staticmethod
    def admins():

        return User.objects.filter(role=User.Role.ADMIN)
