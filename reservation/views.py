from django.shortcuts import render

# Create your views here.
def reservation_index(request):
    return render(request, 'reservation.html')


def reservation_home(request):
    return render(request, 'reserv_home.html')