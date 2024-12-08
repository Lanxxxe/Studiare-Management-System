from django.urls import path, include
from .views import *


urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('reservation_process', reservation_process, name='reservation_process')
]