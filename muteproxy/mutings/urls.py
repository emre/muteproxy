from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.sc_login, name='login'),
    path('logout/', views.sc_logout, name='logout'),
    path('logs/', views.logs, name='logs'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('account/<str:username>/', views.account, name='account'),
]

