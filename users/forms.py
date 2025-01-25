from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                "placeholder": "Enter your password",
            }
        ),
        min_length=8,
        validators=[
            RegexValidator(
                regex=r'^(?=.*\d).+$',
                message="Password must contain at least one number.",
            )
        ],
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 my-2 py-2 mb-4 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                "placeholder": "Confirm your password",
            }
        ),
        min_length=8,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                    "placeholder": "Enter your first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                    "placeholder": "Enter your last name",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                    "placeholder": "Enter your username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                    "placeholder": "Enter your email",
                }
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        # Automatically hash the password
        cleaned_data["password"] = make_password(password)
        return cleaned_data


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                "placeholder": "Enter username or email",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                "placeholder": "Enter your password",
            }
        ),
    )