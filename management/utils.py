from django.shortcuts import redirect
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


