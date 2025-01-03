from django.contrib import admin
from .models import Reservation

class ReservationAdmin(admin.ModelAdmin):
    # Make the user_id field readonly
    readonly_fields = ('reservation_id', 'user', 'space',)
# Register your models here.
admin.site.register(Reservation, ReservationAdmin)