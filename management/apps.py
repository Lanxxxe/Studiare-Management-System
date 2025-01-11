from django.apps import AppConfig
from django.db import connection
from management.utils import create_triggers_for_table


class ManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management'

    def ready(self):
        print('The app is ready')
        def setup_audit_triggers(sender, **kwargs):
            with connection.cursor() as cursor:
                # Get all tables except audit_log and django system tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name NOT LIKE 'sqlite_%'
                    AND name NOT LIKE 'django_%'
                    AND name NOT LIKE 'easyaudit_%'
                    AND name != 'audit_log';
                """)
                tables = cursor.fetchall()
                
                for (table_name,) in tables:
                    for trigger in create_triggers_for_table(table_name):
                        cursor.execute(trigger)

        from django.db.models.signals import post_migrate
        post_migrate.connect(setup_audit_triggers, sender=self)