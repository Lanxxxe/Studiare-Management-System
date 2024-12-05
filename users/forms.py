from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    user_email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'user_email', 'password1', 'password2')

    def check_duplicate_email(self):
        email = self.cleaned_data.get("user_email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("The email you use is already exists.")
        
        return email