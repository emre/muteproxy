from django.core.management.base import BaseCommand, CommandError

from mutings.models import Subscription, Token, Log
from mutings.utils import get_sc_client
import time
import sys

from steemconnect.operations import Mute
from steemconnect.client import Client

from django.core.signing import Signer


class Command(BaseCommand):

    def handle(self, *args, **options):
        sys.stdout.write(f"Started..\n")

        signer = Signer()

        while True:
            subscriptions = Subscription.objects.filter(
                    initial_action=False)
            for subscription in subscriptions:

                token = Token.objects.get(user=subscription.from_user)
                # @todo: check token expire time, and refresh it.
                sc_client = Client(
                    access_token=signer.unsign(token.access_token))

                sys.stdout.write(f"Checking {subscription}\n")

                # flush the cache
                subscription.from_user.fetch_mutings()
                subscription.to_user.fetch_mutings()

                # get the difference
                mute_targets = set(
                    subscription.to_user.muting_list) - set(
                    subscription.from_user.muting_list)

                for mute_target in mute_targets:
                    try:
                        subscription.from_user.mute(mute_target)
                    except Exception as e:
                        sys.stdout.write(str(e) + "\n")
                        continue

                subscription.initial_action = True
                subscription.save()
                sys.stdout.write("Loop is completed. Starting again.")

            sys.stdout.write(f"Sleeping..\n")
            time.sleep(1)