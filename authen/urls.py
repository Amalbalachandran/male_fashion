from . import views
from django.contrib import admin
from django.urls import path
app_name = 'authen'

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
]