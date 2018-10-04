from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.views import auth_logout
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Subscription, Log
from .utils import get_sc_client, get_lightsteem_client


def index(request):
    popular_accounts = get_user_model().objects.filter(
        is_popular=True).order_by("username")

    subscriptions = []
    if request.user.is_authenticated:
        subscriptions = request.user.get_subscriptions()

    return render(request, "index.html", {
        "popular_accounts": popular_accounts,
        "subscriptions": subscriptions,
    })


def sc_login(request):
    if 'code' not in request.GET:
        login_url = get_sc_client().get_login_url(
            redirect_uri=settings.SC_REDIRECT_URI,
            scope="custom_json,offline",
            get_refresh_token=True,
        )
        return redirect(login_url)

    user = authenticate(code=request.GET.get("code"))

    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect("/")
        else:
            return HttpResponse("Account is disabled.")
    else:
        return HttpResponse("Invalid login details.")


def sc_logout(request):
    auth_logout(request)
    return redirect("/")


def check_authentication(request, allowed_methods=None):
    if not allowed_methods:
        allowed_methods = ["POST", ]

    if request.method not in allowed_methods:
        raise Http404

    if not request.user.is_authenticated:
        raise Http404


@csrf_exempt
def subscribe(request):
    check_authentication(request)

    try:
        to_user = get_user_model().objects.get(
            username=request.POST.get("to_user"))
    except get_user_model().DoesNotExist:
        raise Http404

    if to_user == request.user:
        raise Http404

    default_kwargs = {"from_user": request.user, "to_user": to_user}

    try:
        subscription = Subscription.objects.get(**default_kwargs)
    except Subscription.DoesNotExist:
        subscription = Subscription(**default_kwargs)
    subscription.is_active = True
    subscription.save()

    log = Log(
        user=request.user,
        message=f"Subscribed to {to_user}."
    )
    log.save()

    return JsonResponse({"subscribed": to_user.username})


@csrf_exempt
def unsubscribe(request):
    check_authentication(request)

    try:
        to_user = get_user_model().objects.get(
            username=request.POST.get("to_user"))
    except get_user_model().DoesNotExist:
        raise Http404

    if to_user == request.user:
        raise Http404

    default_kwargs = {"from_user": request.user, "to_user": to_user}

    try:
        subscription = Subscription.objects.get(**default_kwargs)
    except Subscription.DoesNotExist:
        raise Http404
    subscription.is_active = False
    subscription.initial_action = False
    subscription.save()

    log = Log(
        user=request.user,
        message=f"Unsubscribed from {to_user}."
    )
    log.save()

    return JsonResponse({"unsubscribed": to_user.username})


def account(request, username):
    try:
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        # check if there is a user like that
        resp = get_lightsteem_client().get_accounts([username])
        if not len(resp):
            return HttpResponse('Invalid user')
        user = get_user_model()(
            username=username
        )
        user.save()

    return render(request, 'account.html', {'account': user})


def logs(request):
    check_authentication(request, allowed_methods=["GET", ])
    logs = Log.objects.filter(user=request.user).order_by("-id")[0:50]
    return render(request, 'logs.html', {'logs': logs})
