from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import  auth, messages
from ..forms import *
from ..models import *
from django.contrib.auth import logout as django_logout
from difflib import SequenceMatcher
import datetime
from django.contrib.auth.decorators import login_required
import operator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView)
from django.db.models import Count
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.decorators import method_decorator
from ..decorators import customer_required
from django.views.decorators.http import require_http_methods
from compression_middleware.decorators import compress_page



class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


@compress_page
def FrontPage(request):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    food = Good.objects.filter(available=True).filter(category__name='packages')
   
   
    advert = HomeAdvert.objects.filter(active=True).order_by('?')[:1]
    
    blog = BlogPost.objects.filter(active=True).order_by('-created_at')

    categories = Category.objects.all()
    goods_by_category = {}

    for category in categories:
        goods_by_category[category] = Good.objects.filter(category=category, available=True)


    
    #food = Good.objects.values('category__name').annotate(dcount=Count('category')).order_by('dcount')
    #print(food)

    sub = SubscriptionPackage.objects.filter()
    context = {'advert': advert, 'food': food, 'blog': blog, 'categories': categories, 'goods_by_category':goods_by_category, 'sub': sub}
    template_name = 'frontpage/index.html'
    return render(request, template_name, context)



def FoodDetails(request, name):
    template_name = 'general/details.html'
    good = get_object_or_404(Good, name=name)
    related = Good.objects.filter().exclude(name=name).order_by('?')[:3]
    context = {'good': good,'related': related}
    return render(request, template_name, context)


def load_vendor(request):
    city_id = request.GET.get('city')
    location = Location.objects.filter(city_id=city_id).order_by('name')
    return render(request, 'customer/vendors.html', {'location': location})






def login(request):
        
    advert = LoginAdvert.objects.filter(active=True).order_by('?')
    

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if form.is_valid():
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                if request.user.is_customer:
                    return redirect('front_page')
                elif request.user.is_bike:
                    return redirect('bike:dashboard')
                                            
        
        else:
            args = {'form': form}
            return render(request, 'registration/login.html', args)

    else:
        form = AuthenticationForm

    args = {'form': form, 'advert': advert}
    return render(request, 'registration/login.html', args)






def CheckUsername(request):
    username = request.POST.get('username')
    if User.objects.filter(username=username).exists():
        return HttpResponse("<div style='color: red;'>The Username is Already Exits</div>")
    else:
        return HttpResponse("<div style='color: green;'>The Username is Available</div>") 
    

def CheckEmail(request):
    email = request.POST.get('email')
    if User.objects.filter(email=email).exists():
        return HttpResponse("The Email is Already Exits")
    else:
        return HttpResponse("The Email is Available")




def AllVendor(request, name):
     template_name = 'general/allvendor.html'
     vendor = Vendor.objects.filter(type__name=name)     
     context = {'vendor': vendor}     
     return render(request, template_name, context)
 
 
 
 
 


def BlogDetails(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)
    recent = BlogPost.objects.filter(active=True).exclude(slug=blog.slug)
    return render(request, 'general/blog_detail.html', {'blog': blog, 'recent': recent})

 
 
 
 

def logout_user(request):
    django_logout(request)
    return redirect('front_page')




def handler404(request, exception):
    context = {}
    response = render(request, "pages/errors/404.html", context=context)
    response.status_code = 404
    return response


def handler500(request):
    context = {}
    response = render(request, "pages/errors/500.html", context=context)
    response.status_code = 500
    return response


