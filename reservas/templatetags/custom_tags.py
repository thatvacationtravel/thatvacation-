from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return None

@register.filter
def add(value, arg):
    try:
        return value + arg
    except (ValueError, TypeError):
        return None

@register.filter
def divide(value, arg):
    try:
        return value / arg
    except (ValueError, TypeError):
        return None
