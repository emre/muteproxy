from django.contrib.auth import get_user_model

from .utils import get_sc_client
from .models import Token
from django.core.signing import Signer

from datetime import datetime, timedelta

class SteemConnectBackend:

    def __init__(self):
        self.signer = Signer()

    def authenticate(self, request, **kwargs):

        if 'username' in kwargs:
            return None

        if 'code' not in kwargs:
            return None

        # validate the access token with /me endpoint and get user information
        client = get_sc_client()

        token_info = client.get_access_token(kwargs.get("code"))
        if 'error' in token_info or 'access_token' not in token_info:
            return None

        user_model = get_user_model()
        try:
            user_instance = user_model.objects.get(
                username=token_info.get("username"))
        except user_model.DoesNotExist:
            user_instance = user_model.objects.create_user(
                username=token_info.get("username"))

        expires_at = datetime.utcnow() + timedelta(
            seconds=token_info.get("expires_in"))

        access_token = self.signer.sign(token_info.get("access_token"))
        refresh_token = self.signer.sign(token_info.get("refresh_token"))

        # add or update the tokens for the user.
        try:
            t = Token.objects.get(user=user_instance)
            t.access_token = access_token
            t.refresh_token = refresh_token
            t.expires_at = expires_at
        except Token.DoesNotExist:
            t = Token(
                user=user_instance,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )

        t.save()

        return user_instance

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None