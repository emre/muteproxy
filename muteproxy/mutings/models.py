import datetime
import json

from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
from django.db import models
from django.utils import timezone
from steemconnect.operations import Mute, Unfollow

from .utils import get_lightsteem_client, get_sc_client


class User(AbstractUser):
    mutings = models.TextField(blank=True, null=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def fetch_mutings(self, dont_save=False):
        c = get_lightsteem_client()
        ignorings = c.account(self.username).ignorings()
        if dont_save:
            return ignorings
        self.mutings = json.dumps(ignorings)
        self.save()

    def get_muting_list(self):
        if not self.mutings:
            return []

        return json.loads(self.mutings)

    @property
    def subscribed_users(self):
        return Subscription.objects.filter(
            from_user=self, is_active=True
        ).values_list('to_user__username', flat=True)

    def get_subscriptions(self):
        return Subscription.objects.filter(from_user=self, is_active=True)

    def refresh_access_token(self):
        signer = Signer()
        token = self.token_set.get()
        sc_client = get_sc_client()
        new_token_data = sc_client.refresh_access_token(signer.unsign(
            token.refresh_token), "custom_json,offline")

        if 'error' in new_token_data:
            # probably access is revoked, let's remove the user's subscriptions.
            Subscription.objects.filter(from_user=self).update(is_active=False)

        token.expires_at = timezone.now() + datetime.timedelta(
            seconds=new_token_data.get("expires_in"))

        token.access_token = signer.sign(new_token_data.get("access_token"))
        token.refresh_token = signer.sign(new_token_data.get("refresh_token"))
        token.save()

    def mute(self, account, courtesy_of=None):
        signer = Signer()
        sc_client = get_sc_client()
        token = self.token_set.get()

        # get a new token in terms of expirations
        if token.expires_at >= timezone.now():
            self.refresh_access_token()
            token = self.token_set.get()

        sc_client.access_token = signer.unsign(
            token.access_token)
        mute_op = Mute(
            self.username,
            account,
        )
        resp = sc_client.broadcast(
            [mute_op.to_operation_structure()])
        if 'error' in resp:
            raise Exception(resp.get("error"))

        if courtesy_of:
            action_text = f"Muted {account} in " \
                          f"courtesy of {courtesy_of}."
        else:
            action_text = f"Muted {account}."

        log = Log(
            user=self,
            message=action_text)
        log.save()

    def unmute(self, account, courtesy_of=None):
        signer = Signer()
        sc_client = get_sc_client()
        token = self.token_set.get()
        sc_client.access_token = signer.unsign(
            token.access_token)

        # Unmute and Unfollow are the same on the blockchain.
        mute_op = Unfollow(
            self.username,
            account,
        )
        resp = sc_client.broadcast(
            [mute_op.to_operation_structure()])
        if 'error' in resp:
            raise Exception(resp.get("error"))

        if courtesy_of:
            action_text = f"Unmuted {account} in " \
                          f"courtesy of {courtesy_of}."
        else:
            action_text = f"Unmuted {account}."

        log = Log(
            user=self,
            message=action_text)
        log.save()


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                  related_name="from_user")
    to_user = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                related_name="to_user")
    is_active = models.BooleanField(default=False)
    initial_action = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.is_active})"


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
