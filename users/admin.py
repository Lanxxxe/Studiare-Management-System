from django.contrib import admin
from .models import User, UserEmail, UserType

# Unregister the existing registration

# Re-register the model (with custom admin settings, if needed)
admin.site.register(User)
admin.site.register(UserEmail)
admin.site.register(UserType)

