from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

def index(request):
    return HttpResponse(f"Pag start ka na earl ha UI {datetime.now()}")


def index(request):
    return render(request, 'studiare_management_system/index.html')
