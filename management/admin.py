from django.contrib import admin
from .models import ManagementUser, HubSpaces, CustomLoginLog

# Register your models here.
admin.site.register(ManagementUser)
admin.site.register(HubSpaces)
admin.site.register(CustomLoginLog)