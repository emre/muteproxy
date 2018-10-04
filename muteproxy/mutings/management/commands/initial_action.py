import sys
import time

from django.core.management.base import BaseCommand
from mutings.models import Subscription


class Command(BaseCommand):

    def handle(self, *args, **options):
        print(f"Started..\n")

        while True:
            subscriptions = Subscription.objects.filter(
                    initial_action=False)
            for subscription in subscriptions:

                print(f"Checking {subscription}\n")

                # flush the cache
                from_user_mutings = subscription.from_user.fetch_mutings(
                    dont_save=True)
                to_user_mutings = subscription.to_user.fetch_mutings(
                    dont_save=True)

                # get the difference
                mute_targets = set(to_user_mutings) - set(from_user_mutings)

                for mute_target in mute_targets:
                    try:
                        subscription.from_user.mute(
                            mute_target,
                            courtesy_of=subscription.to_user.username)
                    except Exception as e:
                        print(str(e) + "\n")
                        continue

                subscription.initial_action = True
                subscription.save()
                print("Loop is completed. Starting again.")

            print(f"Sleeping..\n")
            time.sleep(1)