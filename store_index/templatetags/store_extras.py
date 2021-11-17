from django import template

register = template.Library()

@register.filter(name='cut')
def cut(value):
    """Removes all values of arg from the given string"""
    return value.replace('<ul>', '')