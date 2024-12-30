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
    status = models.CharField(max_length=20, choices=STATUS, blank=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    action = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} by {self.user_id.username}"

