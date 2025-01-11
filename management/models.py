from django.db import models
from django.contrib.auth.models import User
import json

class HubSpaces(models.Model):
    SPACE_STATUS = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Full", "Full"),
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



class AuditLog(models.Model):
    ACTIONS = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    # Primary identifier
    audit_id = models.AutoField(primary_key=True)
    
    # Audit details
    action = models.CharField(max_length=6, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs'
    )
    
    # Data snapshots
    data_before = models.TextField(null=True, blank=True)  # Changed to TextField for SQLite
    data_after = models.TextField(null=True, blank=True)   # Changed to TextField for SQLite
    
    # Additional metadata
    table_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['table_name']),
        ]

    def __str__(self):
        return f"{self.action} on {self.table_name} at {self.timestamp}"

    @property
    def changes(self):
        if self.action != 'UPDATE' or not self.data_before or not self.data_after:
            return None
        
        try:
            before_data = json.loads(self.data_before)
            after_data = json.loads(self.data_after)
            
            changes = {}
            for key in after_data.keys():
                if key in before_data:
                    if before_data[key] != after_data[key]:
                        changes[key] = {
                            'from': before_data[key],
                            'to': after_data[key]
                        }
            return changes
        except json.JSONDecodeError:
            return None







