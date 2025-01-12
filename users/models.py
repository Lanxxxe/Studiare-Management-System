from django.db import models

from management.models import HubSpaces
from django.contrib.auth import get_user_model

User = get_user_model()

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    message = models.TextField()  # Feedback message
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"Feedback from {self.user.username} at {self.created_at}"
