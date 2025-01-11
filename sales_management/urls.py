from django.urls import path, include
from .views import *


urlpatterns = [
    path('', index, name='admin_dashboard'),
    path('sales/', sales, name='admin_sales'),
    path('staff/', staff, name='admin_staff'),
    path('spaces/', spaces, name='admin_spaces'),
    path('transactions/', transactions, name='admin_transaction'),
    path('reservations/', admin_reservations, name='admin_reservations'),
    path('reservations/<str:action>/<int:reservation_id>', update_reservation, name='update_reservation'),
]
