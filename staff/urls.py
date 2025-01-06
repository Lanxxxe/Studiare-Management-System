from django.urls import path, include
from .views import *

urlpatterns = [
    path('', staff_dashboard, name='staff_dashboard'),
    path('staff_spaces/', staff_spaces, name='staff_spaces'),
    path('staff_sales/', staff_sales, name='staff_sales'),
    path('staff_transactions/', staff_transactions, name='staff_transactions'),
    path('staff_reservations/', staff_reservations, name='staff_reservations'),
    path('staff_spaces/sessions/<int:space_id>', staff_manage_sessions, name='manage_sessions'),
    path('staff_spaces/session_receipt/', session_receipt, name='session_receipt'),
]