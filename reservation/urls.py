from django.urls import path, include
from .views import *

urlpatterns = [
    path('', reservation_index, name='reservation_index'),
    path('home/', reservation_home, name='reservation_home'),
]