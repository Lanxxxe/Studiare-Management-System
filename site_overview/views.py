from django.shortcuts import render

# Create your views here.


def landing_page(request):
    return render(request, 'landing_page.html')

def reservation_process(request):
    return render(request, 'reservation_process.html')

def about_us(request):
    return render(request, 'about_us.html')