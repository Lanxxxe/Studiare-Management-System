from django.urls import path, include
from .views import *

urlpatterns = [
    path("", management_index, name="management_index"),
    path('settings/', settings, name='admin_settings'),
    path('settings/account_registration/', account_registration, name='account_registration'),
    path('settings/add_new_space/', add_new_space, name='add_new_space'),
    path('settings/update_staff_account/<int:staff_id>', update_staff_account, name='update_staff_account'),
    path('settings/remove_staff/<int:staff_id>', remove_staff_account, name='remove_staff'),

]



