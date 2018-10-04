from django.contrib import admin

from .models import User, Token, Subscription, Log

admin.site.register(User)
admin.site.register(Token)
admin.site.register(Subscription)
admin.site.register(Log)