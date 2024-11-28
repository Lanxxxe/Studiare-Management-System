from django.db import models

class UserType(models.Model):
    type_id = models.AutoField(primary_key=True)
    user_level = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserType {self.type_id}: Level {self.user_level}"


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    user_email = models.EmailField()
    password = models.CharField(max_length=255)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class UserEmail(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_email = models.EmailField()

    def __str__(self):
        return f"{self.user_id.username}'s Email: {self.user_email}"


class Space(models.Model):
    space_id = models.AutoField(primary_key=True)
    total_space = models.IntegerField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    space_status = models.CharField(max_length=255)

    def __str__(self):
        return f"Space {self.space_id} - {self.location}"


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} by {self.user_id.username}"


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    reservation_date = models.DateTimeField(auto_now_add=True)
    space_reserved = models.ForeignKey(Space, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    accepted_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Reservation {self.reservation_id} for {self.space_reserved}"


class HubSales(models.Model):
    sales_id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    handled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    def __str__(self):
        return f"Sale {self.sales_id}: {self.amount} handled by {self.handled_by.username}"


