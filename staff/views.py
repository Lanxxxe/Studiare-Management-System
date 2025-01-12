from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now, localtime
from django.http import JsonResponse
from django.db.models import Sum, Case, When, Value
from datetime import timedelta

from management.models import HubSpaces
from management.utils import check_staff
from .forms import HubSessionsForm
from django.contrib.auth.models import User

from .models import HubSessions, Transactions
from reservation.models import Reservation
from sales_management.models import DailySales

import sweetify


@check_staff
def staff_dashboard(request):
    spaces = HubSpaces.objects.all()
    reservation = Reservation.objects.filter(status='Pending').count()
    total_vacant_seats = HubSpaces.objects.aggregate(total_vacant=Sum('vacant'))['total_vacant'] or 0
    date_today = localtime().date()

     # Calculate total sales
    total_sales = Transactions.objects.filter(
        check_out_time__date=date_today
    ).aggregate(total_bills=Sum('total_payment'))['total_bills'] or 0


    # Handle AJAX request for date-based filtering
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        date = request.GET.get('date')
        if date:
            reservations = Reservation.objects.filter(reservation_date=date).select_related('space', 'user')
            data = [
                {
                    "reservation_id": r.reservation_id,
                    "space_name": r.space.space_name,
                    "space_type": r.space.space_type,
                    "number_of_seats": r.space.number_of_seats,
                    "status": r.status,
                    "reservation_start_time": r.reservation_start_time.strftime('%H:%M'),
                    "reservation_end_time": r.reservation_end_time.strftime('%H:%M'),
                    "user": r.user.username if r.user else "N/A"
                }
                for r in reservations
            ]
            return JsonResponse(data, safe=False)


    context = {
        "name" : request.session.get("name"),
        'spaces' : spaces,
        'reservations' : reservation,
        'total_vacant_seats' : total_vacant_seats,
        'today_sales' : total_sales,
    }
    return render(request, 'staff_dashboard.html', context)


@check_staff
def staff_spaces(request):
    date_today = localtime().date()

    # Get all reservations for today
    reservations = Reservation.objects.filter(reservation_date=date_today, status='Confirmed')

    # Update the status of HubSpaces
    spaces = HubSpaces.objects.all().order_by('status')

    context = {
        "name" : request.session.get("name"),
        'spaces': spaces,
        'reservations': reservations,
    }

    return render(request, 'staff_spaces.html', context)

@check_staff
def staff_transactions(request):
    # Get the date from the request or use today's date as the default
    selected_date = request.GET.get('filter_date', localtime().date())

    if isinstance(selected_date, str):
        from datetime import datetime
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    # Filter transactions by the selected date
    transactions = Transactions.objects.filter(check_out_time__date=selected_date)

    # Calculate total sales for the selected date
    total_sales = Transactions.objects.filter(
        check_out_time__date=selected_date
    ).aggregate(total_bills=Sum('total_payment'))['total_bills'] or 0

    # Calculate the total time for each transaction
    for transaction in transactions:
        total_time = transaction.check_out_time - transaction.check_in_time
        hours, remainder = divmod(total_time.seconds, 3600)
        minutes = remainder // 60
        transaction.total_time = f"{hours} hours {minutes} minutes"

    total_sales = f"{total_sales:,.2f}"

    # Render the template with context
    context = {
        "name" : request.session.get("name"),
        'transactions': transactions,
        'total_sale': total_sales,
        'selected_date': selected_date,
    }
    return render(request, 'staff_transactions.html', context)


@check_staff
def staff_reservations(request):
    reservation = Reservation.objects.exclude(status="Completed").annotate(
    custom_order=Case(
        When(status="Pending", then=Value(1)),
        When(status="Declined", then=Value(2)),
        When(status="Confirmed", then=Value(3)),
        default=Value(4)  # For other statuses like 'Completed' or 'Cancelled'
        )
    ).order_by('custom_order')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        date = request.GET.get('date')
        if date:
            reservations = Reservation.objects.filter(reservation_date=date).select_related('space', 'user')
            data = [
                {
                    "reservation_id": r.reservation_id,
                    "space_name": r.space.space_name,
                    "space_type": r.space.space_type,
                    "number_of_seats": r.space.number_of_seats,
                    "status": r.status,
                    "reservation_start_time": r.reservation_start_time.strftime('%H:%M'),
                    "reservation_end_time": r.reservation_end_time.strftime('%H:%M'),
                    "user": f'{r.user.first_name} {r.user.last_name}' if r.user else "N/A"
                }
                for r in reservations
            ]
            return JsonResponse(data, safe=False)

    context = {
        "name" : request.session.get("name"),
        'reservations' : reservation,
    }
    return render(request, 'staff_reservations.html', context)


@check_staff
def staff_sales(request):
    today = localtime().date()

    # Get today's transactions
    transactions = Transactions.objects.filter(
        check_out_time__date=today
    ).order_by('-check_in_time')

    # Calculate total sales
    total_sales = Transactions.objects.filter(
        check_out_time__date=today
    ).aggregate(total_bills=Sum('total_payment'))['total_bills'] or 0

    total_sales = f"{total_sales:,.2f}"  # Format total sales

    # Get transaction history
    transaction_history = DailySales.objects.all()

    # Pass context to the template
    context = {
        "name" : request.session.get("name"),
        'transactions': transactions,
        'transaction_history': transaction_history,
        'sales': total_sales,
    }
    return render(request, 'staff_sales.html', context)

@check_staff
def staff_manage_sessions(request, space_id):
    # Get the space and the number of seats
    space = get_object_or_404(HubSpaces, id=space_id)
    number_of_seats = space.number_of_seats
    assigned_staff = get_object_or_404(User, id=request.session.get('user_id'))

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
                    if space.vacant == 0:
                        space.status = "Full"
                    else:
                        space.status = 'Occupied'

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

            # Add extra charges for durations 45 minutes or more
            if minutes >= 45:
                extra_charge = 10 if session.loyalty_card_holder else 20
                payment += extra_charge
            elif minutes >= 20 and minutes < 45:
                extra_charge =  5 if session.loyalty_card_holder else 10
                payment += extra_charge

            # Save transaction and delete session
            Transactions.objects.create(
                guest_name=session.guest_name,
                process_by = assigned_staff,
                space=session.space,
                check_in_time=session.check_in_time,
                check_out_time=session.check_out_time,
                total_payment=payment,
            )

            session.delete()

            # Increase vacancy since session is ended
            space.vacant += 1
            if space.vacant == space.number_of_seats:
                space.status = 'Available'
            elif space.vacant > 0 and space.vacant != space.number_of_seats:
                space.status = 'Occupied'
            space.save()

            # Redirect to receipt page
            return render(request, 'session_receipt.html', {
                'guest_name': session.guest_name,
                'check_in_time': session.check_in_time,
                'check_out_time': session.check_out_time,
                'total_payment': payment,
                'space_id' : space_id
            })

    context = {
        "name" : request.session.get("name"),
        'space': space,
        'forms_with_times': forms_with_times,
        'existing_sessions': existing_sessions,
    }

    return render(request, 'hub_sessions.html', context)


@check_staff
def staff_manage_reservation(request, space_id, reservation_id, action):
    reservation = Reservation.objects.get(reservation_id=reservation_id)
    
    if action == 'ACCEPT':
        reservation.status = 'Confirmed'
        reservation.save()
        sweetify.toast(request, "Reservation Confirmed", icon="success", timer=3000)

        return redirect('staff_reservations')
    
    elif action == 'DECLINED':
        reservation.status = 'Cancelled'
        reservation.save() 
        
        sweetify.toast(request, "Reservation Cancelled", icon="success", timer=3000)
        return redirect('staff_reservations')
    
    elif action == 'REVERT':
        reservation.status = 'Pending'
        reservation.save()
        
        sweetify.toast(request, "Reservation Reverted", icon="success", timer=3000)
        return redirect('staff_reservations')
    
    else:
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
                        if space.vacant == 0:
                            space.status = "Full"
                        else:
                            space.status = 'Occupied'
                        
                        space.save()
                        reservation.status = 'Completed'
                        reservation.save()
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

                # Add extra charges for durations 45 minutes or more
                if minutes >= 45:
                    extra_charge = 10 if session.loyalty_card_holder else 20
                    payment += extra_charge
                elif minutes >= 20 and minutes < 45:
                    extra_charge =  5 if session.loyalty_card_holder else 10
                    payment += extra_charge
                
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
                if space.vacant == space.number_of_seats:
                    space.status = 'Available'
                elif space.vacant > 0 and space.vacant != space.number_of_seats:
                    space.status = 'Occupied'
                space.save()

                # Redirect to receipt page
                return render(request, 'session_receipt.html', {
                    "name" : request.session.get("name"),
                    'guest_name': session.guest_name,
                    'check_in_time': session.check_in_time,
                    'check_out_time': session.check_out_time,
                    'total_payment': payment,
                })

        context = {
            "name" : request.session.get("name"),
            'space': space,
            'forms_with_times': forms_with_times,
            'existing_sessions': existing_sessions,
        }

        return render(request, 'hub_sessions.html', context)


@check_staff
def session_receipt(request):
    return render(request, 'session_receipt.html')