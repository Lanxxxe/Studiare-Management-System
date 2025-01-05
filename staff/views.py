from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from management.models import HubSpaces
from .forms import HubSessionsForm

from .models import HubSessions

import sweetify
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

def staff_spaces(request):
    spaces = HubSpaces.objects.all()

    context = {
        'spaces' : spaces,
    }

    return render(request, 'staff_spaces.html', context)

def staff_transactions(request):
    return render(request, 'staff_transactions.html')

def staff_reservations(request):
    return render(request, 'staff_reservations.html')

def staff_sales(request):
    return render(request, 'staff_sales.html')


def staff_manage_sessions(request, space_id):
    # Get the space and the number of seats
    space = get_object_or_404(HubSpaces, id=space_id)
    print(space)
    number_of_seats = space.number_of_seats

    # Get existing sessions for the space
    existing_sessions = HubSessions.objects.filter(space=space)

    # Create forms for each seat
    forms = []
    for seat_index in range(number_of_seats):
        if seat_index < existing_sessions.count():
            # Pre-fill form with existing session data
            session = existing_sessions[seat_index]
            form = HubSessionsForm(instance=session, prefix=f"form-{seat_index}")
        else:
            # Create an empty form
            form = HubSessionsForm(initial={'space': space}, prefix=f"form-{seat_index}")

        forms.append(form)

    if request.method == 'POST':
        # Identify which form was submitted
        for index, form in enumerate(forms):
            form_prefix = f"form-{index}"
            form = HubSessionsForm(
                request.POST,
                instance=existing_sessions[index] if index < existing_sessions.count() else None,
                prefix=form_prefix,
            )
            if form.is_valid():
                session = form.save(commit=False)  # Do not save to the database yet
                if not session.check_in_time:  # Only set if it's not already populated
                    session.check_in_time = now()  # Set check-in time to the current time
                session.space = space
                space.vacant -= 1
                space.save()
                session.save()  # Save to the database
                sweetify.toast(request, "Session Saved!", timer=2500)
                return redirect('manage_sessions', space_id=space_id)  # Redirect after saving one form
            else:
                # Optionally, show errors for the specific form
                break
    context = {
        'space': space,
        'forms': forms,
    }

    return render(request, 'hub_sessions.html', context)