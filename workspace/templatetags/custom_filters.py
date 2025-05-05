from django import template

register = template.Library()


@register.filter
def dict_get(data, key):
    data = data.get(key)
    return str(data)

