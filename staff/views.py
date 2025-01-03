from django.shortcuts import render

from management.models import HubSpaces

def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

def staff_spaces(request):
    return render(request, 'staff_sales.html')

def staff_sales(request):
    return render(request, 'staff_spaces.html')