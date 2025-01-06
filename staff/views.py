from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta

from management.models import HubSpaces
from management.utils import check_staff
from .forms import HubSessionsForm

from .models import HubSessions, Transactions
from reservation.models import Reservation

import sweetify

@check_staff
def staff_dashboard(request):
    spaces = HubSpaces.objects.all()
    reservation = Reservation.objects.all().count()
    total_vacant_seats = HubSpaces.objects.aggregate(total_vacant=Sum('vacant'))['total_vacant'] or 0

    context = {
        'spaces' : spaces,
        'reservations' : reservation,
        'total_vacant_seats' : total_vacant_seats
    }
    return render(request, 'staff_dashboard.html', context)

@check_staff
def staff_spaces(request):
    spaces = HubSpaces.objects.all()

    context = {
        'spaces' : spaces,
    }

    return render(request, 'staff_spaces.html', context)


@check_staff
def staff_transactions(request):
    date_today = now().date()
    transactions = Transactions.objects.all()
    # Filter transactions for today and calculate the total
    total_bills_today = Transactions.objects.filter(
        check_out_time__date=date_today
    ).aggregate(total_bills=Sum('total_payment'))['total_bills'] or 0
    
    total_bills_today = f"{total_bills_today:.2f}"
    context = {
        'transactions' : transactions,
        'total_sale' : total_bills_today
    }
    return render(request, 'staff_transactions.html', context)


@check_staff
def staff_reservations(request):
    return render(request, 'staff_reservations.html')

@check_staff
def staff_sales(request):
    return render(request, 'staff_sales.html')

@check_staff
def staff_manage_sessions(request, space_id):
    # Get the space and the number of seats
    space = get_object_or_404(HubSpaces, id=space_id)
    number_of_seats = space.number_of_seats

    # Get existing sessions for the space
    existing_sessions = HubSessions.objects.filter(space=space)

    # Create forms for each seat
    forms = []
    remaining_times = []
    for seat_index in range(number_of_seats):
        if seat_index < existing_sessions.count():
            # Pre-fill form with existing session data
            session = existing_sessions[seat_index]
            form = HubSessionsForm(instance=session, prefix=f"form-{seat_index}")
            # Calculate remaining or elapsed time
            if session.session_type == "Open Time":
                elapsed_time = now() - session.check_in_time
                elapsed_time_str = str(elapsed_time).split(".")[0]  # Remove microseconds
                remaining_times.append(f"Time Spent: {elapsed_time_str}")
            else:
                hours = int(session.session_type.split()[0])  # Extract the number of hours
                end_time = session.check_in_time + timedelta(hours=hours)
                remaining_time = end_time - now()
                if remaining_time.total_seconds() > 0:
                    remaining_time_str = str(remaining_time).split(".")[0]  # Remove microseconds
                    remaining_times.append(f"Remaining Time: {remaining_time_str}")
                else:
                    remaining_times.append("Time Over")
        else:
            # Create an empty form
            form = HubSessionsForm(initial={'space': space}, prefix=f"form-{seat_index}")
            remaining_times.append(None)

        forms.append(form)

    # Zip forms and remaining_times for the template
    forms_with_times = zip(forms, remaining_times)

    if request.method == 'POST':
        submitted_form_index = int(request.POST.get("submit", 0)) - 1
        end_session_index = int(request.POST.get("end_session", 0)) - 1

        if submitted_form_index >= 0:
            # Handle Save/Update Session
            form_prefix = f"form-{submitted_form_index}"
            form = HubSessionsForm(
                request.POST,
                instance=existing_sessions[submitted_form_index] if submitted_form_index < existing_sessions.count() else None,
                prefix=form_prefix,
            )
            if form.is_valid():
                session = form.save(commit=False)
                if not session.check_in_time:
                    session.check_in_time = now()
                session.space = space
                if submitted_form_index >= existing_sessions.count():
                    # New session, reduce vacancy
                    space.vacant -= 1
                    space.save()
                session.save()
                sweetify.toast(request, "Session Saved!", timer=2500)
                return redirect('manage_sessions', space_id=space_id)

        if end_session_index >= 0:
            # Handle End Session
            session = existing_sessions[end_session_index]
            session.check_out_time = now()

            # Compute duration and payment
            duration = session.check_out_time - session.check_in_time
            total_seconds = duration.total_seconds()
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            # Determine rate
            rate_per_hour = 10 if session.loyalty_card_holder else 20
            payment = hours * rate_per_hour

            # Save transaction and delete session
            Transactions.objects.create(
                guest_name=session.guest_name,
                space=session.space,
                check_in_time=session.check_in_time,
                check_out_time=session.check_out_time,
                total_payment=payment,
            )
            session.delete()

            # Increase vacancy since session is ended
            space.vacant += 1
            space.save()

            # Redirect to receipt page
            return render(request, 'session_receipt.html', {
                'guest_name': session.guest_name,
                'check_in_time': session.check_in_time,
                'check_out_time': session.check_out_time,
                'total_payment': payment,
            })

    context = {
        'space': space,
        'forms_with_times': forms_with_times,
        'existing_sessions': existing_sessions,
    }

    return render(request, 'hub_sessions.html', context)

@check_staff
def session_receipt(request):
    return render(request, 'session_receipt.html')