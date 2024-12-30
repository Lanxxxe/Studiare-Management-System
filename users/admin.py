from django.contrib import admin
from .models import User, UserEmail

class UserEmailAdmin(admin.ModelAdmin):
    # Make the user_id field readonly
    readonly_fields = ('user_id', 'user_email',)

# Register the model
admin.site.register(User)
admin.site.register(UserEmail, UserEmailAdmin)


