from django.urls import path, include
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("registration/", account_registration, name="registration"),
    path("email_activation/<str:user_id_b64>/<str:token>/", activate_account, name="account_activation"),
    path("accounts/", include("django.contrib.auth.urls"))
]



