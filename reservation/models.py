from django.db import models
from users.models import User 
from management.models import HubSpaces


# Create your models here.
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
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, null=True, default="Pending")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    time_updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Reservation {self.reservation_id} by {self.user}"



