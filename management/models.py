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

    space_name = models.CharField(max_length=30)
    space_type = models.CharField(max_length=20) 
    number_of_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=SPACE_STATUS, default="Available")  # Status of the space
    vacant = models.IntegerField(null=False) 

    def __str__(self):
        return f"{self.space_name} ({self.space_type})"


class CustomLoginLog(models.Model):
    EVENTS = [
        ("Login", "Login"),
        ("Logout", "Logout"),
    ]
    
    log_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=EVENTS, default="")
    ip_address = models.CharField(max_length=100, default="")
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

