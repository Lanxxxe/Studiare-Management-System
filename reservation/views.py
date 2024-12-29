from django.shortcuts import render

# Create your views here.
def reservation_index(request):
    return render(request, 'reservation.html')


def reservation_home(request):
    return render(request, 'reserv_home.html')

def reservation_list(request):
    range_value = range(9)  # This creates a range from 0 to 8 (9 items total)
    context = {
        'range_value': range_value,  # Pass the range itself
        'range_length': len(range_value),  # Pass the length of the range (9 in this case)
    }
    return render(request, 'reservation_list.html', context)

def reservation_transaction(request):
    return render(request, 'reservation_transactions.html')