from django.shortcuts import render

from management.models import HubSpaces

def reservation_index(request):
    return render(request, 'reservation.html')


def reservation_home(request):
    spaces = HubSpaces.objects.all()

    context = {
        "user_name" : request.session.get("name"),
        "spaces" : spaces,
    }
    return render(request, 'reserv_home.html', context)

def reservation_list(request):
    context = {
        "user_name" : request.session.get("name"),
    }
    return render(request, 'reservation_list.html', context)

def reservation_transaction(request):
    context = {
        "user_name" : request.session.get("name"),
    }

    return render(request, 'reservation_transactions.html', context)