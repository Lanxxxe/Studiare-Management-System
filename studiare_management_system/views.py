from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse

from .tokens import activation_token
from .forms import RegistrationForm


def index(request):
    display_message = messages.get_messages(request)

    return render(request, 'index.html', {"message" : display_message})

def login(request):
    display_message = messages.get_messages(request)
    return render(request, 'login.html', {"message": display_message})

def account_registration(request):
    form = RegistrationForm

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Account activation"
            message = render_to_string("account_activation.html", {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': activation_token.make_token(user),
            })

            to_email = form.cleaned_data.get("user_email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            messages.success(request, "Check your email to complete the registration process.")
            return redirect("index")
    return render(request, "registration.html", {"form": form})


def activate_account(request, user_id_b64, token):
    User = get_user_model()

    try:
        user_id = force_str(urlsafe_base64_decode(user_id_b64))
        user = User.objects.get(pk=user_id)
    
    except (TypeError, OverflowError, ValueError, User.DoesNotExist):
        user = None

    if user is not None and activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)

        messages.success(request, "Account activated.")
        return redirect(reverse("login"))
    
    else:
        messages.error(request, "No activation link found.")
        return redirect("index")




