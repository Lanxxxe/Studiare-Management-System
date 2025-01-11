from django.shortcuts import redirect
from django.db import connection
import sweetify

def custom_login_required(view_func):
    """
    Decorator to check if the user is logged in before accessing a page.
    Redirects to the login page if not logged in.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_type"):
            sweetify.error(request, "Access denied!", text="You must be logged in to access the page.", persistent="Got it!")
            return redirect("landing_page") 
        
        elif request.session.get("user_type") == "Staff":
            sweetify.error(request, "Access denied!", text="The page you want to access is for customers.", persistent="Got it!")
            return redirect("staff_dashboard")
        
        elif request.session.get("user_type") == "Admin":
            sweetify.error(request, "Access denied!", text="The page you want to access is for customers.", persistent="Got it!")
            return redirect("admin_dashboard")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_admin(view_func):
    """
    Decorator to check if the user is logged in before accessing a page.
    Redirects to the login page if not logged in.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_type"):  # Check if the user is in the session
            sweetify.error(request, "Access denied!", text="You must be logged in to access the page.", persistent="Got it!")
            return redirect("landing_page")  # Redirect to your login URL
        elif request.session.get("user_type") == "Staff":
            sweetify.error(request, "Access denied!", text="You are prohibited from accessing the page.", persistent="Got it!")
            return redirect("staff_dashboard")
        elif request.session.get("user_type") == "User":
            sweetify.error(request, "Access denied!", text="You are prohibited from accessing the page.", persistent="Got it!")
            return redirect("reservation_home")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_staff(view_func):
    """
    Decorator to check if the user is logged in before accessing a page.
    Redirects to the login page if not logged in.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_type"):  # Check if the user is in the session
            sweetify.error(request, "Access denied!", text="You must be logged in to access the page.", persistent="Got it!")
            return redirect("landing_page")
        elif request.session.get("user_type") == "Admin":
            sweetify.error(request, "Access denied!", text="The page you want to access is at lower level of access. Please use correct account for better management", persistent="Got it!")
            return redirect("admin_dashboard")
        elif request.session.get("user_type") == "User":
            sweetify.error(request, "Access denied!", text="You are prohibited from accessing the page.", persistent="Got it!")
            return redirect("reservation_home")
        return view_func(request, *args, **kwargs)
    
    return wrapper


def get_client_ip(request):
    """Helper function to get the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_current_user(user_id):
    try:
        with connection.cursor() as cursor:
            # Ensure the table exists
            cursor.execute("DELETE FROM current_user_id;")  # Clear existing value
            cursor.execute("INSERT INTO current_user_id (value) VALUES (?);", [user_id])  # Insert new value
    except Exception as e:
        print(f"Error setting current user ID: {e}")


def remove_current_user():
    try:
        with connection.cursor() as cursor:
            # Ensure the table exists
            cursor.execute("DELETE FROM current_user_id;")  # Clear existing value
    except Exception as e:
        print(f"Error setting current user ID: {e}")

def get_table_columns(table_name):
    """Helper function to get column names for a table."""
    with connection.cursor() as cursor:
        return [
            col[1] for col in cursor.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        ]
    

def get_audited_tables():
    """Get list of tables to be audited."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            AND name NOT LIKE 'django_%'
            AND name != 'management_auditlog';
        """)
        return [table[0] for table in cursor.fetchall()]
    
    
def create_triggers_for_table(table_name):
    """Create SQLite triggers for a given table."""
    columns = get_table_columns(table_name)
    
    return [
        # After Insert Trigger
        f"""
        CREATE TRIGGER IF NOT EXISTS {table_name}_audit_insert
        AFTER INSERT ON {table_name}
        BEGIN
            INSERT INTO management_auditlog (
                action,
                table_name, 
                data_after,
                timestamp,
                user_id
            )
            VALUES (
                'CREATE',
                '{table_name}',
                json_object(
                    {', '.join([f"'{col}', NEW.{col}" for col in columns])}
                ),
                CURRENT_TIMESTAMP,
                (SELECT value FROM current_user_id LIMIT 1)
            );
        END;
        """,
        
        # After Update Trigger
        f"""
        CREATE TRIGGER IF NOT EXISTS {table_name}_audit_update
        AFTER UPDATE ON {table_name}
        BEGIN
            INSERT INTO management_auditlog (
                action,
                table_name,
                data_before,
                data_after,
                timestamp,
                user_id
            )
            VALUES (
                'UPDATE',
                '{table_name}',
                json_object(
                    {', '.join([f"'{col}', OLD.{col}" for col in columns])}
                ),
                json_object(
                    {', '.join([f"'{col}', NEW.{col}" for col in columns])}
                ),
                CURRENT_TIMESTAMP,
                (SELECT value FROM current_user_id LIMIT 1)
            );
        END;
        """,
        
        # After Delete Trigger
        f"""
        CREATE TRIGGER IF NOT EXISTS {table_name}_audit_delete
        AFTER DELETE ON {table_name}
        BEGIN
            INSERT INTO management_auditlog (
                action,
                table_name,
                data_before,
                timestamp,
                user_id
            )
            VALUES (
                'DELETE',
                '{table_name}',
                json_object(
                    {', '.join([f"'{col}', OLD.{col}" for col in columns])}
                ),
                CURRENT_TIMESTAMP,
                (SELECT value FROM current_user_id LIMIT 1)
            );
        END;
        """
    ]




