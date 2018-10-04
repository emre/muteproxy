import sys
import time

from django.core.management.base import BaseCommand
from lightsteem.helpers.account import Account
from mutings.models import Subscription, User
from mutings.utils import get_lightsteem_client


class Command(BaseCommand):

    def handle(self, *args, **options):
        lightsteem_client = get_lightsteem_client()
        while True:
            print("Starting..\n")
            self.handle_loop(lightsteem_client)
            print("Sleeping..\n")
            time.sleep(0.5)

    def handle_loop(self, lightsteem_client):
        target_accounts = set(Subscription.objects.filter(
            is_active=True).values_list('to_user__username', flat=True))

        for target_account in target_accounts:
            user = User.objects.get(username=target_account)
            current_muting_list = Account(
                client=lightsteem_client).ignorings(account=target_account)
            old_muting_list = user.get_muting_list()

            # get the fresh new actions
            # unmutes = set(old_muting_list) - set(current_muting_list)
            mutes = set(current_muting_list) - set(old_muting_list)

            # broadcast the changes to all subscribers
            subscriptions = Subscription.objects.filter(
                to_user=user, is_active=True, initial_action=True)
            try:
                for mute in mutes:
                    for subscription in subscriptions:
                        receiver_muting_list = subscription. \
                            from_user.fetch_mutings(dont_save=True)
                        if mute not in receiver_muting_list:
                            print(
                                f"recv: {subscription.from_user} mute {mute} "
                                f"ta: {target_account}")
                            subscription.from_user.mute(
                                mute, courtesy_of=subscription.to_user.username)
            except Exception as e:
                print(e)
