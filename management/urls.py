from django.urls import path, include
from .views import *

urlpatterns = [
    path("", management_index, name="management_index"),
    path('settings/', settings, name='admin_settings'),
]



