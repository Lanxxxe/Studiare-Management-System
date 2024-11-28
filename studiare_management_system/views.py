from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

def index(request):
    return HttpResponse(f"Pag start ka na earl ha UI {datetime.now()}")






