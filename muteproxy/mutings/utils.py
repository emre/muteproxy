
from django.conf import settings
from steemconnect.client import Client
from lightsteem.client import Client as LightsteemClient

_sc_client = None
_lightsteem_client = None


def get_sc_client():
    global _sc_client
    if not _sc_client:
        _sc_client = Client(
            client_id=settings.SC_CLIENT_ID,
            client_secret=settings.SC_CLIENT_SECRET)

    return _sc_client


def get_lightsteem_client():
    global _lightsteem_client
    if not _lightsteem_client:
        _lightsteem_client = LightsteemClient(nodes=settings.STEEM_NODE_LIST)
    return _lightsteem_client
