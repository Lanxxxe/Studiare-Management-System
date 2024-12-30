from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from management.utils import login_required_custom
# Create your views here.

@login_required_custom
def index(request):
    session_user = {
        "user_id" : request.session.get("user_id"),
        "name" : request.session.get("name"),
        "position" : request.session.get("position"),
        "email" : request.session.get("email"),
    }
    return render(request, 'admin_dashboard.html', session_user)

@login_required_custom
def sales(request):

    return render(request, 'admin_sales.html')

@login_required_custom
def spaces(request):
    

    return render(request, 'admin_spaces.html')

@login_required_custom
def staff(request):

    return render(request, 'admin_staff.html')

