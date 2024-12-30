from django.urls import path, include
from .views import *


urlpatterns = [
    path('', index, name='admin_dashboard'),
    path('sales/', sales, name='admin_sales'),
    path('staff/', staff, name='admin_staff'),
    path('spaces/', spaces, name='admin_spaces'),
    
]
