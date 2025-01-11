from django.db import models
from django.contrib.auth.models import User
from management.models import HubSpaces

class Reservation(models.Model):
    RESERVATION_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    reservation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    space = models.ForeignKey(HubSpaces, on_delete=models.CASCADE, null=True)
    reservation_date = models.DateField()
    reservation_start_time = models.TimeField(null=True)
    reservation_end_time = models.TimeField(null=True)
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS, default="Pending")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation by {self.user}"
