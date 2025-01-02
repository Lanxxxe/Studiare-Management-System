from django.urls import path, include
from .views import *

urlpatterns = [
    path('', staff_dashboard, name='staff_dashboard'),
    path('staff_sales', staff_sales, name='staff_sales'),
    path('staff_spaces', staff_spaces, name='staff_spaces'),
]