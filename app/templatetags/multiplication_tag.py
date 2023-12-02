from django import template

register = template.Library()

@register.filter
def addition(value, arg):
    return int(value) + int(arg)



@register.filter
def multiply(value, arg):
    return value * arg