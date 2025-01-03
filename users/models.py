from django.db import models

from management.models import HubSpaces

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    user_email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({'Active' if self.is_active else 'Inactive'})"


class UserEmail(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_email = models.EmailField()

    def __str__(self):
        return f"{self.user_id.username}'s Email: {self.user_email}"
