from django.urls import path, include
from .views import *
from reservation.views import *

urlpatterns = [
    path("", index, name="index"),
    path("registration/", account_registration, name="registration"),
    path("login/", login, name='login'),
    path("forgot_password/", forgot_password, name='forgot_password'),
    path('reset_password/<int:user_id>/<str:token>/', reset_password, name='reset_password'),
    path("email_activation/<uid>/", activate_account, name="account_activation"),
    path("logout/", logout, name="logout"),
]



