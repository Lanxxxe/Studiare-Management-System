from django.shortcuts import render, redirect, get_object_or_404
from management.utils import check_admin
# Create your views here.

# from sales_management
from management.models import ManagementUser, HubSpaces
from reservation.models import Reservation

import sweetify

@check_admin
def index(request):
    spaces = HubSpaces.objects.all()
    reservations = Reservation.objects.all().count()
    active_staffs = ManagementUser.objects.filter(status="Duty").count()
    context = {
        "user_id" : request.session.get("user_id"),
        "name" : request.session.get("name"),
        "position" : request.session.get("position"),
        "email" : request.session.get("email"),
        'spaces' : spaces,
        "active_staffs" : active_staffs,
        "reservations" : reservations,
    }
    return render(request, 'admin_dashboard.html', context)

@check_admin
def sales(request):
    reservations = Reservation.objects.all().count()

    context = {
        'reservations' : reservations,
    }
    return render(request, 'admin_sales.html', context)

@check_admin
def spaces(request):
    spaces = HubSpaces.objects.all()
    context = {
        'spaces' : spaces
    }

    return render(request, 'admin_spaces.html', context)

@check_admin
def staff(request):
    user_id = request.session.get('user_id')
    staffs = ManagementUser.objects.exclude(id=user_id)

    context = {
        'staffs' : staffs
    }
    return render(request, 'admin_staff.html', context)



@check_admin
def admin_reservations(request):
    reservations = Reservation.objects.all()

    context = {
        'reservations' : reservations,
    }
    return render(request, 'admin_reservations.html', context)


@check_admin
def update_reservation(request, action, reservation_id):
    

    update_reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if action == 'CONFIRM':
        update_reservation.status = 'Confirmed'
        update_reservation.save()
        sweetify.toast(request, "Reservation Confirmed", icon="success", timer=3000)
        
    elif action == 'DECLINED':
        update_reservation.status = 'Cancelled'
        update_reservation.save()
        sweetify.toast(request, "Reservation Cancelled", icon="success", timer=3000)
    
    elif action == 'UNDO':
        update_reservation.status = 'Pending'
        update_reservation.save()
        sweetify.toast(request, "Action Reverted", icon="success", timer=3000)

    else:
        sweetify.toast(request, "Invalid Action", icon="error", timer=3000)

    return redirect('admin_reservations')
