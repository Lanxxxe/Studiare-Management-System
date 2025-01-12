from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value
from django.contrib.auth.hashers import check_password, make_password
from management.models import HubSpaces
from management.utils import custom_login_required
from django.contrib.auth.models import User, AnonymousUser
from .models import Reservation
from staff.models import Transactions

from django.contrib import messages
from users.models import Feedback
from management.forms import UpdateUserForm, UpdatePasswordForm

import sweetify
from datetime import datetime, date, timedelta

def reservation_index(request):
    return render(request, 'reservation.html')


def user_feedback(request):
    if request.method == 'POST':
        feedback_message = request.POST.get('message')  # Get feedback input
        
        if feedback_message.strip():  # Ensure input is not empty
            Feedback.objects.create(
                user_id=request.session.get("id"),  # Link feedback to the logged-in user
                message=feedback_message.strip(),
            )
            sweetify.success(request, "Thank you for your feedback!")
            return redirect('reservation_home')  # Redirect to home or any other page
        else:
            messages.error(request, "Feedback cannot be empty.")

    context = {
        "user_name" : request.session.get("name"),
    }
    return render(request, 'feedback.html', context)


def user_profile(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)

    # Forms for updating user information and password
    user_form = UpdateUserForm(instance=user)
    password_form = UpdatePasswordForm()

    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UpdateUserForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                sweetify.success(request, "Updated!", text="Information updated successfully!", persistent="Okay")
                return redirect('user_profile')

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
                    return redirect('user_profile')
                else:
                    sweetify.error(request, "Error", text="Incorrect current password.", persistent="Return")
            else:
                sweetify.error(request, "Error", text="Password form is invalid. Please try again.", persistent="Return")

    context = {
        "user_name" : request.session.get("name"),
        'user_form': user_form,
        'password_form': password_form,
    }

    return render(request, 'user_account.html', context)




@custom_login_required
def reservation_home(request):
    user_id = request.session.get("id")
    spaces = HubSpaces.objects.all().order_by('status').values()
    reservations = Reservation.objects.filter(user=user_id).count()
    transactions = Reservation.objects.filter(user=user_id, status='Completed').count()
    context = {
        "user_name" : request.session.get("name"),
        "spaces" : spaces,
        "reservation" : reservations,
        "type" : request.session.get("user_type"),
        "transaction" : transactions
    }
    return render(request, 'reserv_home.html', context)

@custom_login_required
def reservation_list(request):
    user_id = request.session.get("id")
    reservations = Reservation.objects.filter(user=user_id)
    
    context = {
        "user_name" : request.session.get("name"),
        "reservations" : reservations,
    }
    return render(request, 'reservation_list.html', context)

@custom_login_required
def reservation_transaction(request):
    user_id = request.session.get("id")
    reservations = Reservation.objects.filter(user=user_id).annotate(
    custom_order=Case(
        When(status="Pending", then=Value(1)),
        When(status="Declined", then=Value(2)),
        When(status="Confirmed", then=Value(3)),
        default=Value(4)  # For other statuses like 'Completed' or 'Cancelled'
        )
    ).order_by('custom_order')
    
    # Compute total time for each reservation
    reservations_with_time = []
    for reservation in reservations:
        if reservation.reservation_start_time and reservation.reservation_end_time:
            # Calculate the time difference
            start_time = datetime.combine(datetime.min, reservation.reservation_start_time)
            end_time = datetime.combine(datetime.min, reservation.reservation_end_time)
            total_time = end_time - start_time  # This is a timedelta object
        else:
            total_time = None  # Handle missing start or end time

        # Append reservation and total time to the list
        reservations_with_time.append({
            "reservation": reservation,
            "total_time": total_time,
        })
        
    context = {
        "user_name" : request.session.get("name"),
        "reservations" : reservations,
        'transactions' : reservations_with_time,
    }

    return render(request, 'reservation_transactions.html', context)

@custom_login_required
def reserve_space(request, space_id, reservation_id=None):        
    user_id = request.session.get("id")
    user = get_object_or_404(User, id=user_id)
    space = get_object_or_404(HubSpaces, id=space_id)
    current_reservation = None

    if reservation_id:
        current_reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

    if request.method == "POST":
        # Get form data
        if isinstance(request.user, AnonymousUser):
            print("Anonymous User - not linked to CRUD events")
        else:
            print(f"Authenticated User: {request.user}")
        checkin_date = request.POST.get("checkin_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # Validate form data
        if not checkin_date or not start_time or not end_time:
            sweetify.error(request, "All fields are required.")
            if reservation_id:
                return redirect("update_reserve_space", space_id=space_id, reservation_id=reservation_id)
            else:
                return redirect("reserve_space", space_id=space_id)

        # Combine date and time into datetime objects
        try:
            checkin_datetime = datetime.strptime(f"{checkin_date} {start_time}", "%Y-%m-%d %H:%M")
            checkout_datetime = datetime.strptime(f"{checkin_date} {end_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            sweetify.error(request, "Invalid date or time format.")
            if reservation_id:
                return redirect("update_reserve_space", space_id=space_id, reservation_id=reservation_id)
            else:
                return redirect("reserve_space", space_id=space_id)

        # Check if the end time is after the start time
        if checkin_datetime >= checkout_datetime:
            sweetify.error(request, "Checkout time must be after check-in time.")
            if reservation_id:
                return redirect("update_reserve_space", space_id=space_id, reservation_id=reservation_id)
            else:
                return redirect("reserve_space", space_id=space_id)

        # Check for overlapping reservations
        overlapping_reservations = Reservation.objects.filter(
            space=space,
            reservation_date=checkin_date,
            reservation_start_time__lt=checkout_datetime.time(),
            reservation_end_time__gt=checkin_datetime.time()
        )


        if overlapping_reservations.exists():
            sweetify.error(request, "The selected time slot is already reserved.")
            if reservation_id:
                return redirect("update_reserve_space", space_id=space_id, reservation_id=reservation_id)
            else:
                return redirect("reserve_space", space_id=space_id)

        # Create or update the reservation
        if current_reservation:
            # Update existing reservation
            current_reservation.reservation_date = checkin_date
            current_reservation.reservation_start_time = checkin_datetime.time()
            current_reservation.reservation_end_time = checkout_datetime.time()
            current_reservation.save()
            sweetify.success(request, "Reservation successfully updated!")
        else:
            # Create new reservation
            Reservation.objects.create(
                user=user,
                space=space,
                reservation_date=checkin_date,
                reservation_start_time=checkin_datetime.time(),
                reservation_end_time=checkout_datetime.time(),
            )

            sweetify.success(request, "Reservation successfully created!", button="Great!")


        return redirect("reservation_home")  # Redirect to the reservation home page

    context = {
        "user_name": request.session.get("name"),
        "user": user,
        "space": space,
        "reservation" : current_reservation,
        "date_today" : (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    return render(request, 'reserv_space.html', context)


@custom_login_required
def remove_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

    if reservation.user.id != request.session.get("id"):
        sweetify.error(request, "You do not have permission to delete this reservation.", button="Okay")
        return redirect("landing_page") 

    if request.method == "POST":
        reservation.delete()
        sweetify.success(request, "Reservation successfully deleted!", button="Okay")
        return redirect("reservation_list")

    context = {
        "reservation": reservation,
    }
    return render(request, "delete_reservation.html", context)


