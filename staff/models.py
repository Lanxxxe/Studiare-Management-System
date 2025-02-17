from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

from management.models import HubSpaces
from sales_management.models import DailySales

class HubSessions(models.Model):
    LOYALTY_STATUS = [
        (True, "Yes"),
        (False, "No"),
    ]

    SESSION_TYPE = [
        ("Open Time", "Open Time"),
        ("1 Hour", "1 Hour"),
        ("2 Hours", "2 Hours"),
        ("3 Hours", "3 Hours"),
        ("4 Hours", "4 Hours"),
        ("5 Hours", "5 Hours"),
        ("6 Hours", "6 Hours"),
        ("7 Hours", "7 Hours"),
        ("8 Hours", "8 Hours"),
        ("9 Hours", "9 Hours"),
        ("10 Hours", "10 Hours"),
        ("11 Hours", "11 Hours"),
        ("12 Hours", "12 Hours"),
    ]

    guest_name = models.CharField(max_length=100)
    space = models.ForeignKey(HubSpaces, on_delete=models.CASCADE, related_name="sessions") 
    check_in_time = models.DateTimeField(default=now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    loyalty_card_holder = models.BooleanField(choices=LOYALTY_STATUS, default=False)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE, default="Open Time")  # Type of session (Open/Duration)

    def __str__(self):
        return f"{self.guest_name} - {self.space}"

class Transactions(models.Model):
    guest_name = models.CharField(max_length=100, blank=True, null=True)
    process_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="processed_transactions",
        null=True
    )
    space = models.ForeignKey(HubSpaces, on_delete=models.SET_NULL, null=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction: {self.guest_name} - {self.space} - {self.total_payment}"

