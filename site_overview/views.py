from django.shortcuts import render

def index(request):
    display_message = messages.get_messages(request)

    return render(request, 'index.html', {"message" : display_message})

