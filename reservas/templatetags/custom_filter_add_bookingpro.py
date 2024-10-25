from django import template

register = template.Library()



@register.filter(name='add')
def add(value1, value2):
    """Suma dos valores con redondeo a dos decimales."""
    try:
        return round(value1 + value2, 2)
    except TypeError:
        return 0


@register.simple_tag
def add_to_total(current_total, value):
    return current_total + value



