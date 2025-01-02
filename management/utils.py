from django.shortcuts import redirect
import sweetify

def login_required_custom(view_func):
    """
    Decorator to check if the user is logged in before accessing a page.
    Redirects to the login page if not logged in.
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):  # Check if the user is in the session
            sweetify.error(request, "Access denied!", text="You must be logged in to access the page.", persistent="Got it!")
            return redirect("landing_page")  # Redirect to your login URL
        return view_func(request, *args, **kwargs)
    
    return wrapper