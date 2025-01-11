from django.contrib import admin
from .models import HubSpaces, CustomLoginLog, AuditLog

# Register your models here.
# admin.site.register(HubSpaces)
admin.site.register(CustomLoginLog)
admin.site.register(AuditLog)