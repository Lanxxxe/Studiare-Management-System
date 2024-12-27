from django.db import models
from users.models import User 

# Create your models here.

class Space(models.Model):
    space_id = models.AutoField(primary_key=True)
    total_space = models.IntegerField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    space_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Space {self.space_id} - {self.location}"


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    reservation_date = models.DateTimeField(auto_now_add=True)
    space_reserved = models.ForeignKey(Space, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    accepted_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Reservation {self.reservation_id} for {self.space_reserved}"

