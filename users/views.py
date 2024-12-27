from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .tokens import activation_token
from .forms import RegistrationForm, LoginForm
from .models import User, UserType


def index(request):
    display_message = messages.get_messages(request)

    return render(request, 'login.html', {"message" : display_message})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]

            try:
                user = User.objects.get(
                    username=identifier if User.objects.filter(username=identifier).exists() else
                    User.objects.get(user_email=identifier)
                )
                if user.is_active and check_password(password, user.password):
                    # Add session or token logic here as needed
                    messages.success(request, f"Welcome {user.firstname}!")
                    return redirect("index")  # Replace with your home URL
                elif not user.is_active:
                    messages.error(request, "Account is not active. Please confirm your email.")
                else:
                    messages.error(request, "Invalid credentials.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def account_registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False

            # Automatically set the user_type to "User"
            try:
                default_user_type = UserType.objects.get(user_level="User")
                user.user_type = default_user_type
            except UserType.DoesNotExist:
                messages.error(request, "Default user type 'User' is not defined.")
                return redirect("registration")

            user.save()

            # Send email confirmation
            uid = urlsafe_base64_encode(force_bytes(user.user_id))
            activation_link = request.build_absolute_uri(
                reverse("account_activation", kwargs={"uid": uid})
            )
            send_mail(
                subject="Account Activation",
                message=f"Click the link to activate your account: {activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.user_email],
            )
            messages.success(request, "Account created. Please check your email to confirm.")
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "registration.html", {"form": form})


def activate_account(request, uid):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(user_id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. You can now log in.")
        return redirect("login")
    except User.DoesNotExist:
        messages.error(request, "Invalid activation link.")
        return redirect("registration")




