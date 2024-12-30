from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from management.utils import login_required_custom

from .models import ManagementUser
from .forms import LoginForm, UpdatePasswordForm, UpdateUserForm

import sweetify

def management_index(request):

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)  # Bind POST data to the form
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            try:
                user = ManagementUser.objects.get(username=username)
                # if check_password(password, user.password):
                if user.password == password:
                    if user.position in ["Staff", "Admin"]:
                        # Save user information in session
                        request.session['user_id'] = user.id
                        request.session['name'] = f'{user.first_name} {user.last_name}'
                        request.session['position'] = user.position
                        request.session['email'] = user.email

                        sweetify.success(request, "Welcome back!",  text=f"Hello, {user.first_name}!", button=True)

                        # Redirect based on user position
                        if user.position == "Admin" or user.position == "Staff":
                            return redirect("admin_dashboard")
                    else:
                        sweetify.error(
                            request, 
                            "Access Denied",
                            text="You're prohibited from accessing this page.", 
                            button=True
                        )
                else:
                    sweetify.error(request, "Invalid password", text="Please check your password", button=True)
            except ManagementUser.DoesNotExist:
                sweetify.error(request, "User not found", text="Please check your username or password", persistent="Back")

    return render(request, 'manage_login.html', {"form": form})


@login_required_custom
def settings(request):
    # Retrieve the currently logged-in user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        sweetify.error(request, "You are not logged in.")
        return redirect('login')  # Redirect to login if not authenticated

    # Fetch the user object
    user = get_object_or_404(ManagementUser, id=user_id)
    staffs = ManagementUser.objects.exclude(id=user_id)

    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UpdateUserForm(request.POST, instance=user)
            password_form = UpdatePasswordForm()
            if user_form.is_valid():
                user_form.save()
                sweetify.success(request, "Updated!", text="Information updated successfully!", persistent="Okay")
                return redirect('admin_settings')
        elif 'update_password' in request.POST:
            user_form = UpdateUserForm(instance=user)
            password_form = UpdatePasswordForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                if user.password == current_password:  # Compare plain text password (not recommended)
                    user.password = make_password(password_form.cleaned_data['new_password'])  # Hash the new password
                    user.save()
                    sweetify.success(request, "Updated!", text="Password updated successfully!", persistent="Okay")
                    return redirect('admin_settings')
                else:
                    sweetify.error(request, "Error", text="Incorrect current password.", persistent="Return")

            else:
                sweetify.error(request, "Error", text="Password do not match. Please try again", persistent="Return")
    else:
        user_form = UpdateUserForm(instance=user)
        password_form = UpdatePasswordForm()

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'staffs' : staffs
        
    }
    return render(request, 'admin_settings.html', context)










