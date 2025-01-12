from django import template

register = template.Library()

@register.filter
def rating(value):
    """Return a range up to the given value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)