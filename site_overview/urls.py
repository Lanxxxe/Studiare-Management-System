from django.urls import path, include
from .views import *


urlpatterns = [
    path('', landing_page, name='landing_page'),
]