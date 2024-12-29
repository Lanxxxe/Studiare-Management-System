from django.shortcuts import render

# Create your views here.
def reservation_index(request):
    return render(request, 'reservation.html')


def reservation_home(request):
    return render(request, 'reserv_home.html')

def reservation_list(request):
    context = {
        'range_value': range(9)  # Replace 3 with your desired number of rectangles
    }
    return render(request, 'reservation_list.html', context)

def reservation_transaction(request):
    return render(request, 'reservation_transactions.html')