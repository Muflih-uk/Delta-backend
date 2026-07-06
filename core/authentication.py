from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.supabase import supabase

User = get_user_model()


class SupabaseAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(
        self,
        request,
    ) -> Optional[Tuple[User, None]]:

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2:
            raise AuthenticationFailed("Invalid Authorization header.")

        if parts[0] != self.keyword:
            return None

        access_token = parts[1]

        try:
            response = supabase.auth.get_user(access_token)

        except Exception:
            raise AuthenticationFailed("Invalid or expired access token.")

        if response.user is None:
            raise AuthenticationFailed("Invalid user.")

        supabase_uid = response.user.id

        try:
            user = User.objects.get(supabase_uid=supabase_uid)

        except User.DoesNotExist:
            raise AuthenticationFailed("User does not exist.")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        return (user, None)

    def authenticate_header(self, request):
        return self.keyword
