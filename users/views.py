from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User, Permission
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .forms import RegistrationForm, LoginForm

from management.models import CustomLoginLog
from management.utils import get_client_ip, set_current_user, remove_current_user
import sweetify

# Temporary storage for password reset tokens (in production, use a database or cache)
password_reset_tokens = {}

def index(request):
    display_message = messages.get_messages(request)

    return render(request, 'login.html', {"message" : display_message})

def login(request):
    # sweetify.success(request, 'You did it', text='Good job! You successfully showed a SweetAlert message', persistent='Hell yeah')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=identifier, password=password)

            try:
                if user:
                    if user.is_active:
                        auth_login(request, user)  # Login the user
                        request.session['user_id'] = user.id
                        request.session['username'] = user.username
                        request.session['name'] = f"{user.first_name} {user.last_name}"
                        request.session['email'] = user.email
                        request.session['user_type'] = "User"
                        set_current_user(user.id)
                        # Log the login event
                        CustomLoginLog.objects.create(
                            username=user.username,
                            user="User",
                            action="Login",
                            ip_address=get_client_ip(request),
                        )

                        sweetify.success(request, f"Welcome {user.first_name}!", persistent="Got it!")
                        return redirect("reservation_home")  # Replace with your home URL
                    else:
                        sweetify.error(request, "Account is not active. Please confirm your email.", persistent="Okay")
                else:
                    sweetify.error(request, "Invalid username/email or password.", persistent="Okay")
            except User.DoesNotExist:
                sweetify.error(request, "User not found.", persistent="Okay")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def account_registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Send email confirmation
            uid = urlsafe_base64_encode(force_bytes(user.id))
            activation_link = request.build_absolute_uri(
                reverse("account_activation", kwargs={"uid": uid})
            )
            send_mail(
                subject="Account Activation",
                message=f"Click the link to activate your account: {activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            sweetify.success(request, "Account created. Please check your email to confirm.", persistent="Okay")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "registration.html", {"form": form})


def activate_account(request, uid):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        # Assign "add_reservation" permission
        permission = Permission.objects.get(codename='add_reservation')
        user.user_permissions.add(permission)
        sweetify.success(request, "Account activated. You can now log in.", persistent="Okay")
        return redirect("login")
    except User.DoesNotExist:
        sweetify.error(request, "Invalid activation link.", persistent="Okay")
        return redirect("registration")


def logout(request):
    try:
        CustomLoginLog.objects.create(
            username=request.session.get("username"),
            user=request.session.get("user_type"),
            action="Logout",
            ip_address=get_client_ip(request)
        )
        remove_current_user()
        if request.session.get("user_type") in ["Staff", "Admin"]:

            request.session.flush()
            sweetify.success(request, "Logout Successfully.", persistent="Okay")
            return redirect("management_index")
        
        request.session.flush()
        sweetify.success(request, "Logout Successfully.", persistent="Okay")
    except:
        pass
    return redirect("landing_page")


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()

        try:
            # Check if user exists
            user = User.objects.get(username=username, email=email)

            # Generate a unique token
            token = get_random_string(50)

            password_reset_tokens[user.id] = token

            # Construct reset URL
            reset_url = request.build_absolute_uri(
                reverse("reset_password", kwargs={"user_id": user.id, "token" : token})                
                )

            # Send email with the reset link
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link below to reset your password:\n\n{reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            sweetify.success(request, 'Sent successfully!', text='A password reset link has been sent to your email.', persistent="Got it!")
            return redirect('login')

        except User.DoesNotExist:
            sweetify.error(request, 'Error', text='No account found with the provided username and email.', persistent="Okay")
    print(password_reset_tokens)
    return render(request, 'forgot_password.html')



def reset_password(request, user_id, token):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            try:
                # Verify the token
                if password_reset_tokens.get(int(user_id)) == token:
                    user = User.objects.get(id=user_id)
                    user.password = make_password(new_password)
                    user.save()

                    # Remove the token after use
                    del password_reset_tokens[int(user_id)]

                    sweetify.success(request,  'Password successfully reset!', text='Password successfully reset. You can now log in.', persistent="Got it!")
                    return redirect('login')
                else:
                    sweetify.error(request, 'Error', text='Invalid or expired reset token.', persistent="Okay")
            except User.DoesNotExist:
                sweetify.error(request, 'Error', text='User not found.', persistent="Okay")
        else:
            sweetify.error(request, 'Error', text='Passwords do not match.',  persistent="Okay")
    print(password_reset_tokens)
    return render(request, 'reset_password.html')




