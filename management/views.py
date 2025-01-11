from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# from easyaudit.models import CRUDEvent, LoginEvent
from management.utils import check_admin, get_client_ip, set_current_user
from .models import HubSpaces, CustomLoginLog, AuditLog
from .forms import LoginForm, RegistrationForm, UpdatePasswordForm, UpdateUserForm, AddNewSpaceForm, UpdateStaffAccountForm, UpdateSpaceForm


import sweetify, json, pytz

def management_index(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)  # Bind POST data to the form
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Use Django's `authenticate` method to validate username and password
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user has staff or superuser privileges
                if user.is_staff or user.is_superuser:
                    login(request, user)  # Log in the user
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    request.session['name'] = f'{user.first_name} {user.last_name}'
                    request.session['user_type'] = "Admin" if user.is_superuser else "Staff"
                    request.session['email'] = user.email
                    set_current_user(user.id)
                    # Record login (Optional logging, depends on your needs)
                    CustomLoginLog.objects.create(
                        username=user.username,
                        user="Admin" if user.is_superuser else "Staff",
                        action="Login",
                        ip_address=get_client_ip(request)
                    )

                    sweetify.success(request, "Welcome back!", text=f"Hello, {user.first_name}!", button=True)
                    
                    # Redirect based on user type
                    if user.is_superuser:
                        return redirect("admin_dashboard")
                    else:
                        return redirect("staff_dashboard")
                else:
                    sweetify.error(
                        request,
                        "Access Denied",
                        text="You're prohibited from accessing this page.",
                        button=True
                    )
            else:
                sweetify.error(request, "Invalid credentials", text="Please check your username or password", persistent="Back")

    return render(request, 'manage_login.html', {"form": form})

@check_admin
def settings(request):
    # Retrieve the currently logged-in user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        sweetify.error(request, "You are not logged in.")
        return redirect('login')  # Redirect to login if not authenticated

    # Fetch the user object
    user = get_object_or_404(User, id=user_id)
    staffs = User.objects.filter(is_staff=True).exclude(id=user_id)
    spaces = HubSpaces.objects.all().order_by('space_name').values()
    
    # Forms for updating user information and password
    user_form = UpdateUserForm(instance=user)
    password_form = UpdatePasswordForm()

    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UpdateUserForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                sweetify.success(request, "Updated!", text="Information updated successfully!", persistent="Okay")
                return redirect('admin_settings')

        elif 'update_password' in request.POST:
            password_form = UpdatePasswordForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']

                # Check current password
                if check_password(current_password, user.password):
                    # Set the new password (hashed)
                    user.password = make_password(new_password)
                    user.save()
                    sweetify.success(request, "Updated!", text="Password updated successfully!", persistent="Okay")
                    return redirect('admin_settings')
                else:
                    sweetify.error(request, "Error", text="Incorrect current password.", persistent="Return")
            else:
                sweetify.error(request, "Error", text="Password form is invalid. Please try again.", persistent="Return")

    context = {
        "name" : request.session.get("name"),
        'user_form': user_form,
        'password_form': password_form,
        'staffs': staffs,
        'spaces': spaces,
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
                # print(registration_form.position)
                registration_form.save()
                sweetify.success(request, "Registration Complete!", text="New account created successfully!", persistent="Okay")
                return redirect('admin_settings')
    else:
        registration_form = RegistrationForm()

    context = {
        "name" : request.session.get("name"),
        "form" : registration_form,
    }   

    return render(request, 'acc_registration.html', context)


@check_admin
def update_staff_account(request, staff_id):
    #Retrieve staff
    staff = User.objects.get(id=staff_id)

    if request.method == "POST":
        form = UpdateStaffAccountForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            sweetify.success(request, "Updated", text=f"Staff {staff.first_name} {staff.last_name} updated successfully!", persistent="Okay")
            return redirect('admin_settings')  # Replace 'staff_list' with your desired redirect URL
        else:
            sweetify.error(request, "Failed to update staff details. Please check the form.")
    else:
        form = UpdateStaffAccountForm(instance=staff)
    
    context = {
        "name" : request.session.get("name"),
        'staff' : staff,
        'form' : form,
    }    

    return render(request, 'update_staff.html', context)


@check_admin
def remove_staff_account(request, staff_id):
    staff = get_object_or_404(User, id=staff_id)
    try:
        staff.delete()
        sweetify.toast(request, f"Staff {staff.first_name} {staff.last_name} has been removed.", icon="success")
    except:
        sweetify.error(request, "Failed to remove staff account. Please check the staff details.")
    
    return redirect('admin_settings') 


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

    context = {
        "name" : request.session.get("name"),
        "forms" : add_new_space_form
    }

    return render(request, 'add_new_space.html', context)


@check_admin
def update_space_information(request, space_id):
    space = HubSpaces.objects.get(id=space_id)

    if request.method == "POST":
        form = UpdateSpaceForm(request.POST, instance=space)
       
        if form.is_valid():
            updated_space = form.save(commit=False)
            occupied_seats = space.number_of_seats - space.vacant
            
            # Rule: Prevent decreasing the number of seats below occupied seats
            if space.status == "Full" or space.status == "Occupied":
                # Rule: Prevent decreasing seats if the space is full
                sweetify.error(
                    request,
                    f"Failed to update. Space is still {space.status}."
                )
                return redirect('update_space_information', space_id=space_id)
                
            # Save the updated space if rules are satisfied
            updated_space.save()
            sweetify.success(request, "Updated", text=f"Space updated successfully!", persistent="Okay")
            return redirect('admin_settings')
        else:
            sweetify.error(request, "Failed to update space details. Please check the form.")
    else:
        form = UpdateSpaceForm(instance=space)

    context = {
        "name": request.session.get("name"),
        "form": form
    }
    return render(request, 'update_space.html', context)

@check_admin
def remove_space(request, space_id):
    space = HubSpaces.objects.get(id=space_id)
    try:
        # Rule: Prevent deletion if the space is occupied
        if space.status == "Occupied" or space.status == "Full":
            sweetify.error(
                request,
                f"Failed to remove space '{space.space_name}'. Space is currently occupied.",
                persistent="Okay"
            )
            return redirect('admin_settings')
        else:
            # space.delete()
            sweetify.toast(request, f"Space removed successfully!", icon="success", timer=2500)
    except Exception as e:
        sweetify.error(request, f"An error occurred while removing the space: {str(e)}")

    return redirect('admin_settings')

@check_admin
def audit_trail(request, event_id=None):
    if event_id:
        try:
            audit_detail = AuditLog.objects.get(audit_id=event_id)
            
            context = {
                "name": request.session.get("name"),
                'detail': audit_detail,
                'data_before': json.loads(audit_detail.data_before) if isinstance(audit_detail.data_before, str) else audit_detail.data_before,
                'data_after': json.loads(audit_detail.data_after) if isinstance(audit_detail.data_after, str) else audit_detail.data_after
            }
            return render(request, 'audit_detail.html', context)
        except AuditLog.DoesNotExist:
            return render(request, 'audit_detail.html', status=404)
    else:
        # Constants
        ITEMS_PER_PAGE = 15
        crud_events_filter = ['management_auditlog', 'management_customloginlog', 'easyaudit_requestevent', 
                            'easyaudit_crudevent', 'easyaudit_loginevent', 'current_user_id']

        # Get page numbers from request
        login_page = request.GET.get('login_page', 1)
        crud_page = request.GET.get('crud_page', 1)

        # Query all events
        login_events = CustomLoginLog.objects.order_by('-action_date')
        crud_events = AuditLog.objects.exclude(table_name__in=crud_events_filter).order_by('-timestamp')

        # Create paginators
        login_paginator = Paginator(login_events, ITEMS_PER_PAGE)
        crud_paginator = Paginator(crud_events, ITEMS_PER_PAGE)

        try:
            login_events_page = login_paginator.page(login_page)
        except PageNotAnInteger:
            login_events_page = login_paginator.page(1)
        except EmptyPage:
            login_events_page = login_paginator.page(login_paginator.num_pages)

        try:
            crud_events_page = crud_paginator.page(crud_page)
        except PageNotAnInteger:
            crud_events_page = crud_paginator.page(1)
        except EmptyPage:
            crud_events_page = crud_paginator.page(crud_paginator.num_pages)

        # Format CRUD events
        formatted_crud_events = []
        ph_timezone = pytz.timezone("Asia/Manila")

        for event in crud_events_page:
            ph_timestamp = event.timestamp.astimezone(ph_timezone)
            formatted_timestamp = ph_timestamp.strftime("%B %d %Y, %I:%M %p").lower()

            formatted_crud_events.append({
                "audit_id": event.audit_id,
                "user": event.user if event.user else "System",
                "action": event.action,
                "table_name": event.table_name,
                "data_before": json.loads(event.data_before) if event.data_before else None,
                "data_after": json.loads(event.data_after) if event.data_after else None,
                "formatted_timestamp": formatted_timestamp,
            })

        context = {
            "name": request.session.get("name"),
            "login_events": login_events_page,
            "crud_events": formatted_crud_events,
            "login_events_page": login_events_page,
            "crud_events_page": crud_events_page,
        }
        return render(request, 'audit_trail.html', context)



