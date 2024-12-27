from django.urls import path, include
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("registration/", account_registration, name="registration"),
    path("login/", login, name='login'),
    path("email_activation/<uid>/", activate_account, name="account_activation"),
    # path("accounts/", include("django.contrib.auth.urls"))
]



