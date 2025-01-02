from django.db import models

class ManagementUser(models.Model):
    POSITIONS = [
        ("Staff", "Staff"),
        ("Admin", "Admin"),
    ]

    STATUS = [
        ("Duty", "Duty"),
        ("Absent", "Absent"),
        ("Rest Day", "Rest Day"),
        ("On Leave", "On Leave"),

    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=25, unique=True)
    position = models.CharField(max_length=10, choices=POSITIONS)
    status = models.CharField(max_length=20, choices=STATUS, default="New Hired")
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class HubSpaces(models.Model):
    SPACE_STATUS = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Reserved", "Reserved"),
    ]

    space_name = models.CharField(max_length=30)  # Name of the space
    space_type = models.CharField(max_length=20)  # Type of the space
    number_of_seats = models.PositiveIntegerField()  # Number of seats
    status = models.CharField(max_length=10, choices=SPACE_STATUS, default="Available")  # Status of the space

    def __str__(self):
        return f"{self.space_name} ({self.space_type}) - {self.status}"


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} by {self.user_id.username}"

