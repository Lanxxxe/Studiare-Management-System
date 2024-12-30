from django import forms
from django.contrib.auth.hashers import make_password
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                "placeholder": "Enter your password",
            }
        ),
        min_length=8,
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
        fields = ['firstname', 'lastname', 'username', 'user_email', 'password']
        widgets = {
            "firstname": forms.TextInput(
                attrs={
                    "class": "w-full px-4 my-2 py-2 border border-[#f6d5b4] text-black rounded-md focus:outline-none focus:ring-2 focus:ring-[#e09247]",
                    "placeholder": "Enter your first name",
                }
            ),
            "lastname": forms.TextInput(
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
            "user_email": forms.EmailInput(
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
        cleaned_data["password"] = make_password(password)  # Hash the password
        return cleaned_data


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email",
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
