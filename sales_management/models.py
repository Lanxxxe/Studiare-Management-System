from django.db import models
from users.models import User

# Create your models here.
class HubSales(models.Model):
    sales_id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    handled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    def __str__(self):
        return f"Sale {self.sales_id}: {self.amount} handled by {self.handled_by.username}"
