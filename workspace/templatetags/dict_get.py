from django import template

register = template.Library()


@register.filter
def dict_get(data, key):
    return data.get(key)

