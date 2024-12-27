from django.db import models

class UserType(models.Model):
    type_id = models.AutoField(primary_key=True)
    user_level = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UserType {self.type_id}: Level {self.user_level}"


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    user_email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({'Active' if self.is_active else 'Inactive'})"


class UserEmail(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_email = models.EmailField()

    def __str__(self):
        return f"{self.user_id.username}'s Email: {self.user_email}"


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    action_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Log {self.log_id} by {self.user_id.username}"

