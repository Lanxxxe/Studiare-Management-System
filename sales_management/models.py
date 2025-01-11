from django.db import models

# Create your models here.
class DailySales(models.Model):
    sales_date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False 
        db_table = 'daily_sales'