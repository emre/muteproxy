import sys
import time

from django.core.management.base import BaseCommand
from mutings.models import Subscription


class Command(BaseCommand):

    def handle(self, *args, **options):
        sys.stdout.write(f"Started..\n")

        while True:
            subscriptions = Subscription.objects.filter(
                    initial_action=False)
            for subscription in subscriptions:

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