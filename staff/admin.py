from django.contrib import admin
from .models import HubSessions, Transactions
from management.models import HubSpaces

admin.site.register(HubSessions)
admin.site.register(Transactions)
admin.site.register(HubSpaces)