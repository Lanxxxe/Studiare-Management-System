from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from management.utils import login_required_custom
# Create your views here.

# from sales_management
from management.models import ManagementUser, HubSpaces

@login_required_custom
def index(request):
    spaces = HubSpaces.objects.all()
    active_staffs = ManagementUser.objects.filter(status="Duty").count()
    context = {
        "user_id" : request.session.get("user_id"),
        "name" : request.session.get("name"),
        "position" : request.session.get("position"),
        "email" : request.session.get("email"),
        'spaces' : spaces,
        "active_staffs" : active_staffs,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required_custom
def sales(request):
    return render(request, 'admin_sales.html')

@login_required_custom
def spaces(request):
    spaces = HubSpaces.objects.all()
    context = {
        'spaces' : spaces
    }

    return render(request, 'admin_spaces.html', context)

@login_required_custom
def staff(request):
    user_id = request.session.get('user_id')
    staffs = ManagementUser.objects.exclude(id=user_id)

    context = {
        'staffs' : staffs
    }
    return render(request, 'admin_staff.html', context)

