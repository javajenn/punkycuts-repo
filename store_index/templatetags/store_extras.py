from django import template

register = template.Library()

@register.filter(name='cut')
def cut(value):
    """Removes all values of arg from the given string"""
    return value.replace('<ul>', '')

@register.filter
def get_obj_attr(obj, attr):
    return obj[attr]

@register.filter
def state_taxes(value):
    taxes = float(value) * .0575
    return taxes

@register.filter
def total_taxes(value):
    taxes = float(value) * .0575
    return float(value) + float(taxes)