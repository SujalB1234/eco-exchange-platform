from django import template

register = template.Library()

@register.simple_tag
def user_greeting(user):
    """Returns a proper greeting for the user"""
    if user.get_full_name().strip():
        return user.get_full_name()
    return user.username