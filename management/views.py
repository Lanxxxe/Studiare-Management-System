from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from easyaudit.models import CRUDEvent, RequestEvent
from management.utils import check_admin, get_client_ip

from .models import ManagementUser, HubSpaces, CustomLoginLog
from .forms import LoginForm, RegistrationForm, UpdatePasswordForm, UpdateUserForm, AddNewSpaceForm, UpdateStaffAccountForm, UpdateSpaceForm


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
                        request.session['username'] = user.username
                        request.session['name'] = f'{user.first_name} {user.last_name}'
                        request.session['user_type'] = user.position
                        request.session['email'] = user.email
                        sweetify.success(request, "Welcome back!",  text=f"Hello, {user.first_name}!", button=True)
                        
                        CustomLoginLog.objects.create(
                            username=user.username,
                            user=user.position,
                            action="Login",
                            ip_address=get_client_ip(request)
                        )

                        # Redirect based on user position
                        if user.position == "Admin":
                            return redirect("admin_dashboard")
                        
                        elif user.position == "Staff":
                            return redirect("staff_dashboard")
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

@check_admin
def settings(request):
    # Retrieve the currently logged-in user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        sweetify.error(request, "You are not logged in.")
        return redirect('login')  # Redirect to login if not authenticated

    # Fetch the user object
    user = get_object_or_404(ManagementUser, id=user_id)
    staffs = ManagementUser.objects.exclude(id=user_id)
    spaces = HubSpaces.objects.all()

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
        'staffs' : staffs,
        'spaces' : spaces,
        
    }
    return render(request, 'admin_settings.html', context)


@check_admin
def account_registration(request):
    # Retrieve the currently logged-in user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        sweetify.error(request, "You are not logged in.")
        return redirect('login')  # Redirect to login if not authenticated

    if request.method == 'POST':
        if 'register_new_account' in request.POST:
            registration_form = RegistrationForm(request.POST)
            if registration_form.is_valid():
                registration_form.save()
                sweetify.success(request, "Registration Complete!", text="New account created successfully!", persistent="Okay")
                return redirect('admin_settings')
    else:
        registration_form = RegistrationForm()

    return render(request, 'acc_registration.html', {"forms": registration_form})


@check_admin
def update_staff_account(request, staff_id):
    #Retrieve staff
    staff = ManagementUser.objects.get(id=staff_id)

    if request.method == "POST":
        form = UpdateStaffAccountForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            sweetify.success(request, "Updated", text=f"Staff {staff.first_name} {staff.last_name} updated successfully!", persistent="Okay")
            return redirect('admin_staff')  # Replace 'staff_list' with your desired redirect URL
        else:
            sweetify.error(request, "Failed to update staff details. Please check the form.")
    else:
        form = UpdateStaffAccountForm(instance=staff)
    context = {
        'staff' : staff,
        'form' : form,
    }    

    return render(request, 'update_staff.html', context)


@check_admin
def remove_staff_account(request, staff_id):
    staff = get_object_or_404(ManagementUser, id=staff_id)
    try:
        staff.delete()
        sweetify.toast(request, f"Staff {staff.first_name} {staff.last_name} has been removed.", icon="success")
    except:
        sweetify.error(request, "Failed to remove staff account. Please check the staff details.")
    
    return redirect('admin_staff') 

@check_admin
def add_new_space(request):
    # Retrieve the currently logged-in user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        sweetify.error(request, "You are not logged in.")
        return redirect('login')  # Redirect to login if not authenticated
    
    if request.method == 'POST':
        if 'add_new_space' in request.POST:
            add_new_space_form = AddNewSpaceForm(request.POST)
            if add_new_space_form.is_valid():
                # Create a new HubSpaces instance but don't save it to the database yet
                new_space = add_new_space_form.save(commit=False)
                
                # Set the 'vacant' field to the value of 'number_of_seats'
                new_space.vacant = new_space.number_of_seats
                
                # Save the instance to the database
                new_space.save()
                sweetify.success(request, "New Space Added!", text="New space added successfully!", persistent="Okay")
                return redirect('admin_settings')
            else:
                sweetify.error(request, "Form submission failed!", text="Please check the form and try again.")
    else:
        add_new_space_form = AddNewSpaceForm()

    return render(request, 'add_new_space.html', {"forms": add_new_space_form})


@check_admin
def update_space_information(request, space_id):
    space = HubSpaces.objects.get(id=space_id)

    if request.method == "POST":
        form = UpdateSpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            sweetify.success(request, "Updated", text=f"Space updated successfully!", persistent="Okay")
            return redirect('admin_settings')
        else:
            sweetify.error(request, "Failed to update space details. Please check the form.")
    else:
        form = UpdateSpaceForm(instance=space)

    context = {
        'form' : form
    }
    return render(request, 'update_space.html', context)


@check_admin
def remove_space(request, space_id):
    space = HubSpaces.objects.get(id=space_id)

    try:
        space.delete()
        sweetify.toast(request,f"Space removed successfully!", icon="success", timer=2500)
    except Exception as e:
        sweetify.error(request, "Failed to remove space. Please check the form.")

    return redirect('admin_settings')
    

@check_admin
def audit_trail(request):
    # Querying recent audit events
    login_events = CustomLoginLog.objects.all()  # Last 10 login/logout events
    crud_events = CRUDEvent.objects.order_by('-datetime')[:10]    # Last 10 CRUD events
    request_events = RequestEvent.objects.order_by('-datetime')[:10]  # Last 10 URL requests
    
    # Passing the data to the template
    context = {
        'login_events': login_events,
        'crud_events': crud_events,
        'request_events': request_events,
    }
    return render(request, 'audit_trail.html', context)

