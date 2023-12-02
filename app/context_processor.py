from unicodedata import category, name
from django.http import response
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.contrib.auth import login
from django.db.models import Count


def get_data(request):
    
    
    settings = Settings.objects.filter().first()
    PAY_STACK_KEY = 'pk_test_804847426746912fbe07c2a2e5ebedcc127e1f90' 
    categories = Category.objects.all()
    duration = OpenHours.objects.all() 
    if(request.user.id):
        user_order = Order.objects.filter(user=request.user, paid=False).first()  
        

        return {'user_order': user_order, 'categories': categories, 'duration': duration, 'settings': settings, 'PAY_STACK_KEY': PAY_STACK_KEY}
    return{'settings': settings, 'categories': categories, 'duration': duration, 'PAY_STACK_KEY': PAY_STACK_KEY}

  
    
        




 




