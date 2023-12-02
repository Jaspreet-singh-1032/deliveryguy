from django import template
from app.models import Order, Category
from django.contrib.auth import login

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, paid=False)
        if qs.exists():
            return qs[0].items.count()
    return 0



 
        
