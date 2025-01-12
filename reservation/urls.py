from django.urls import path, include
from .views import *

urlpatterns = [
    path('', reservation_index, name='reservation_index'),
    path('profile/', user_profile, name='user_profile'),
    path('home/', reservation_home, name='reservation_home'),
    path('transactions/', reservation_transaction, name='reservation_transcation'),
    path('users_reservations/', reservation_list, name='reservation_list'),
    path('user_feedback/', user_feedback, name='user_feedback'),
    path('reserve_space/<int:space_id>/<int:reservation_id>/', reserve_space, name='update_reserve_space'),
    path('reserve_space/<int:space_id>/', reserve_space, name='reserve_space'),
    path('remove_reservation/<int:reservation_id>/', remove_reservation, name='remove_reservation'),

]