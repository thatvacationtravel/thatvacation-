from django import template
import urllib.parse
import math

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    return getattr(obj, attr_name, None)



@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def floor(value):
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return value



@register.filter
def ceil(value):
    try:
        return math.ceil(value)
    except (ValueError, TypeError):
        return value


@register.filter
def add_to_list(value, list_):
    if value not in list_:
        list_.append(value)
    return list_

@register.filter
def add_to_set(current_set, value):
    current_set.add(value)
    return current_set


@register.filter(name='url_replace')
def url_replace(value):
    # Evitamos codificar espacios ya codificados
    return value.replace("%2520", "%20").replace("%2520", "%20")

@register.filter
def url_unquote(value):
    return urllib.parse.unquote(value)