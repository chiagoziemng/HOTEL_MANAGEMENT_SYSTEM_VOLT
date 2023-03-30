from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def removetags(value):
    """Removes HTML tags from the given value."""
    return strip_tags(value)
