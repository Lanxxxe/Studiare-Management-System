from django.shortcuts import render, redirect, get_object_or_404

from management.models import HubSpaces
from users.models import User
from .models import Reservation

import sweetify
from datetime import datetime

def reservation_index(request):
    return render(request, 'reservation.html')


def reservation_home(request):
    user_id = request.session.get("id")
    spaces = HubSpaces.objects.all()
    reservations = Reservation.objects.filter(user=user_id).count()

    context = {
        "user_name" : request.session.get("name"),
        "spaces" : spaces,
        "reservation" : reservations,
    }
    return render(request, 'reserv_home.html', context)

def reservation_list(request):
    user_id = request.session.get("id")
    reservations = Reservation.objects.filter(user=user_id)

    context = {
        "user_name" : request.session.get("name"),
        "reservations" : reservations,
    }
    return render(request, 'reservation_list.html', context)

def reservation_transaction(request):
    user_id = request.session.get("id")
    reservations = Reservation.objects.filter(user=user_id)

    context = {
        "user_name" : request.session.get("name"),
        "reservations" : reservations,
    }

    return render(request, 'reservation_transactions.html', context)

def reserve_space(request, space_id):        
    user_id = request.session.get("id")
    user = get_object_or_404(User, user_id=user_id)
    space = get_object_or_404(HubSpaces, id=space_id)

    if request.method == "POST":
        # Get form data
        checkin_date = request.POST.get("checkin_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # Validate form data
        if not checkin_date or not start_time or not end_time:
            sweetify.error(request, "All fields are required.")
            return redirect("reserve_space", space_id=space_id)

        # Combine date and time into datetime objects
        try:
            checkin_datetime = datetime.strptime(f"{checkin_date} {start_time}", "%Y-%m-%d %H:%M")
            checkout_datetime = datetime.strptime(f"{checkin_date} {end_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            sweetify.error(request, "Invalid date or time format.")
            return redirect("reserve_space", space_id=space_id)

        # Check if the end time is after the start time
        if checkin_datetime >= checkout_datetime:
            sweetify.error(request, "Checkout time must be after check-in time.")
            return redirect("reserve_space", space_id=space_id)

        # Check for overlapping reservations
        overlapping_reservations = Reservation.objects.filter(
            space=space,
            reservation_start_time=checkout_datetime,
            reservation_end_time=checkin_datetime
        )
        if overlapping_reservations.exists():
            sweetify.error(request, "The selected time slot is already reserved.")
            return redirect("reserve_space", space_id=space_id)

        # Create and save the reservation
        reservation = Reservation.objects.create(
            user=user,
            space=space,
            reservation_date= checkin_date,
            reservation_start_time=checkin_datetime,
            reservation_end_time=checkout_datetime
        )
        sweetify.success(request, "Reservation successfully created!")
        return redirect("reservation_home")  # Redirect to the reservation home page
    context = {
        "user_name" : request.session.get("name"),
        "user" : user,
        "space" : space,
    }
    return render(request, 'reserv_space.html', context)