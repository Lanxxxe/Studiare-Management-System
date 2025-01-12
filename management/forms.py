from django import forms
from .models import HubSpaces
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



class RegistrationForm(UserCreationForm):
    POSITION_CHOICES = [
        ("", "Select Position"),
        ("Admin", "Admin"),
        ("Staff", "Staff"),
    ]

    position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400',
            }
        ),
        required=True
    )

    contact_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400",
                "placeholder": "Enter your contact number",
            }
        ),
        required=True
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300',
                'placeholder': 'Enter your password',
            }
        ), 
        min_length=8,
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300',
                'placeholder': 'Confirm your password',
            }
        ),
        min_length=8,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "contact_number", "position", "password1", "password2"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter your first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter your last name",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter your username",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter your email",
                }
            ),
        }

    def clean_position(self):
        position = self.cleaned_data.get("position")
        if not position:
            raise forms.ValidationError("Position is required.")
        return position

    def save(self, commit=True):
        # Call the base class's save to get the user instance
        user = super().save(commit=False)
        position = self.cleaned_data.get('position')

        # Set staff/admin attributes based on the position
        if position == "Admin":
            user.is_staff = True
            user.is_superuser = True
        elif position == "Staff":
            user.is_staff = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "my-3 block w-full mb-4 px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-white rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                "placeholder": "Username",
            }
        ),
        required=True,
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "my-3 block w-full mb-4 px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-white rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                "placeholder": "Password",
            }
        ),
        required=True,
        label="Password"
    )



class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', "username", 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'})


class UpdatePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'}),
        label="New Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'}),
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data


class AddNewSpaceForm(forms.ModelForm):
    class Meta:
        model = HubSpaces
        fields = ["space_name", "space_type", "number_of_seats",]
        widgets = {
            "space_name": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the space name",
                }
            ),
            "space_type": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the space type",
                }
            ),
            "number_of_seats":forms.NumberInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the number of seats",
                }
            ),
        }


class UpdateStaffAccountForm(forms.ModelForm):
    POSITION_CHOICES = [
        ("", "Select Position"),
        ("Admin", "Admin"),
        ("Staff", "Staff"),
    ]

    position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400',
            }
        ),
        required=True
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'}),
        label="Password",
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # Pre-fill position based on `is_staff` and `is_superuser` attributes
        if user_instance:
            if user_instance.is_superuser:
                self.fields['position'].initial = "Admin"
            elif user_instance.is_staff:
                self.fields['position'].initial = "Staff"
            else:
                self.fields['position'].initial = ""
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'})

    def save(self, commit=True):
        # Call the base class's save to get the user instance
        user = super().save(commit=False)
        position = self.cleaned_data.get('position')

        # Set staff/admin attributes based on the position
        if position == "Admin":
            user.is_staff = True
            user.is_superuser = True
        elif position == "Staff":
            user.is_staff = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user

class UpdateSpaceForm(forms.ModelForm):
    class Meta:
        model = HubSpaces
        fields = ['space_name', 'space_type', 'number_of_seats']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'})



