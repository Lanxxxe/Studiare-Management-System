from django import forms
from .models import ManagementUser, HubSpaces

class RegistrationForm(forms.ModelForm):
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
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300',
                'placeholder': 'Enter the password',
            },
        ), 
        min_length=8, 
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300',
                'placeholder': 'Enter the password',
            },
        ), 
        min_length=8, 
    )

    class Meta:
        model = ManagementUser
        fields = ["first_name", "last_name", "contact_number", "email", "username", "position", "password"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the last name",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the email",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                    "placeholder": "Enter the username",
                }
            ),
        }


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "my-3 block w-full mb-4 px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-white rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                "placeholder": "Username",
            }
        ),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "my-3 block w-full mb-4 px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-white rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-pink-400 placeholder-gray-300",
                "placeholder": "Password",
            }
        ), 
        label="Password", 
        required=True
    )


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = ManagementUser
        fields = ['first_name', 'last_name', "username", 'contact_number', 'email',  "position"]

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

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'}),
        label="Password"
    )

    class Meta:
        model = ManagementUser
        fields = ['first_name', 'last_name', 'contact_number', 'email', 'username', 'position']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'})






