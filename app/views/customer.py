from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.contrib.auth.forms import PasswordChangeForm
from ..decorators import customer_required
from ..forms import *
from ..models import *
from django.contrib.messages.views import SuccessMessageMixin
import random
import string
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import (View, CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView)
from datetime import datetime
from django.db.models import Count
import requests
from django.http import HttpResponseRedirect
from django.http import Http404
from django.db.models import Q
import googlemaps 
from compression_middleware.decorators import compress_page
import os
from num2words import num2words
import httpx
from twilio.rest import Client
from infobip_api_client.api_client import ApiClient, Configuration
from django.conf import settings as conf_settings
from django.http import HttpResponse
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST



gmaps = googlemaps.Client(key=conf_settings.GOOGLE_API)  
SECKEY = conf_settings.PAY_STACK_SECRET





sms_api = '5EWcNg002bHka0U2yVt00wPpTOdsrJRXZGNhGdfDsDnh8pCJw03HXaFSOTbk&from=DELIVERYGUY'



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def random_string():
    value = 'DISHAXIS-'
    return value + str(random.randint(10000, 99999))

@compress_page
@login_required
def CustomerDashboard(request):
    category = Category.objects.all()
    context = {'category': category}
    return render(request, 'customer/dashboard.html', context)

@method_decorator([compress_page], name='dispatch')
class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        p = ProfileCustomer.objects.get(user=self.request.user.id)
        return redirect('customer:customer_profile', p.id)


@compress_page
def CustomerProfile(request, pk):
    template_name = 'customer/editprofile.html'
    customer = get_object_or_404(ProfileCustomer, pk=pk)
    form = CustomerProfileForm(request.POST or None, request.FILES or None, instance = customer)
    if request.method == 'POST':
        if form.is_valid():
            p = form.save(commit=False)
            p.save()
            messages.success(request, "Your Profile Was Updated Successfully...")
            return redirect('front_page')
    return render(request, template_name, {'form': form})


@compress_page
def AllRestaurants(request):
    template_name = 'customer/restaurants.html'
    current_time = datetime.now().time() 
    good = Good.objects.order_by('?')
    banner = Vendor.objects.order_by('?').first()
    restaurant = Vendor.objects.all() 
    context = {'restaurant': restaurant, 'banner': banner, 'current_time': current_time, 'good': good}
    return render(request, template_name, context)


@login_required
def AllVendorGoods(request, pk):
    template_name = 'customer/vendorgoods.html'
    vendor = get_object_or_404(Vendor, pk=pk)
    image = VendorImageGallery.objects.select_related('vendor').all()
    comment = VendorComment.objects.select_related('vendor').all()

    try:
        order = Order.objects.filter(user=request.user, paid=False).first()
    except Order.DoesNotExist:
        order = None
    
    formcomment = VendorCommentForm()

    if request.method=='POST' and 'BtnComment' in request.POST:
        formcomment = VendorCommentForm(request.POST)
        if formcomment.is_valid():
            formcomment = VendorCommentForm(request.POST)
            comment = formcomment.save(commit=False)  
            comment.user = request.user
            new_vendor = Vendor.objects.filter(pk=vendor.pk).first()
            comment.vendor = new_vendor
            comment.save()
            
            messages.info(request, "Item added to your cart")
            return redirect(request.META['HTTP_REFERER']) 

    else:
        formcomment = VendorCommentForm()
    '''
    if request.method=='POST' and 'btnform2' in request.POST:
    do something...
    ''' 
    

    good = Good.objects.select_related('vendor').filter(vendor=vendor.pk)

    context = {'good': good, 'vendor': vendor, 'object': order, 'image': image, 'comment': comment, 'formcomment': formcomment}
    return render(request, template_name, context)




@compress_page
@login_required
def Checkout(request):

    templates_name = 'checkout.html'
    order = Order.objects.get(user=request.user, paid=False)
    context = {'order': order}
    return render(request, templates_name, context)







@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Good, pk=pk)
   
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False,
    )
  
    
    order_qs = Order.objects.filter(user=request.user, paid=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            if order_item.item.addon and order_item.item.delivery:
                return redirect('app:add-on-package', order_item.pk) 
            elif order_item.item.addon or order_item.item.delivery:
                 return redirect('app:add-on-package', order_item.pk) 
            else:
                return redirect(request.META['HTTP_REFERER'])  
          
        else:
            order.items.add(order_item)
            if order_item.item.addon and order_item.item.delivery:
                return redirect('app:add-on-package', order_item.pk) 
            elif order_item.item.addon or order_item.item.delivery:
                 return redirect('app:add-on-package', order_item.pk) 
            else:
                return redirect(request.META['HTTP_REFERER']) 
            return redirect('app:add-on-package', order_item.pk)
           
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        if order_item.item.addon and order_item.item.delivery:
            return redirect('app:add-on-package', order_item.pk) 
        elif order_item.item.addon or order_item.item.delivery:
           return redirect('app:add-on-package', order_item.pk) 
        else:
            return redirect(request.META['HTTP_REFERER']) 
        
    





@login_required
def add_to_cart_plugin(request, pk, food_pk):
    item = get_object_or_404(PluginFoods, pk=pk)
    food = Good.objects.filter(pk=food_pk).first()
   
    order_item, created = PluginOrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False,
        foods = food,
    )
  
    
    order_qs = OrderItem.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.plugin.filter(item__pk=item.pk, foods__id=food.pk).exists():
            order_item.quantity += 1
            order_item.save()
            return redirect(request.META['HTTP_REFERER'])  
          
        else:
            order.plugin.add(order_item)
            return redirect(request.META['HTTP_REFERER'])
           
    else:
        ordered_date = timezone.now()
        order = OrderItem.objects.create(user=request.user, ordered_date=ordered_date)
        order.plugin.add(order_item)
        return redirect(request.META['HTTP_REFERER']) 






  
@require_POST
@login_required
def plus_to_cart(request, pk):
    item = get_object_or_404(Good, pk=pk)
   
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False,
    )

    
    order_qs = Order.objects.filter(user=request.user, paid=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            return redirect(request.META['HTTP_REFERER'])  
          
        else:
            order.items.add(order_item)
            return redirect(request.META['HTTP_REFERER']) 
           
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect(request.META['HTTP_REFERER']) 
        




@login_required
def AddonWithPackage(request, pk):
    # Get the existing OrderItem
    templates_name = 'customer/addonitem.html'
    order_item = get_object_or_404(OrderItem, pk=pk)
    
    goods = Good.objects.all()
    
    addon = AddonGoods.objects.all()
    delivery = DeliveryPackages.objects.all()
    
    
    
    all_foods = PluginFoods.objects.all()

    # Create an empty list to store dictionaries
    food_details = []
    
    
    selected_addons = order_item.addon.all() if order_item else []
       

    # Loop through each food item
    for food in all_foods:
        # Get related PluginOrderItem instances where ordered is False
        order_items = PluginOrderItem.objects.filter(item=food, foods=order_item.item.pk, ordered=False)
        #print(order_items)
        # Get total quantity for the specific food
        total_quantity = sum(order_item.quantity for order_item in order_items)

        # Append data to the list as a dictionary
        food_details.append({
            'food_name': food.name,
            'food_price': food.price,
            'food_pk': food.pk,
            'total_quantity': total_quantity
        })
    
    
    

   
    #addonform = AddonForm(request.POST or None)
    if 'Progress' in request.POST:
        
        if order_item.item.delivery == True and order_item.item.addon == False:

            # Assuming you get the selected DeliveryPackage and AddonGoods from form data or somewhere else
            delivery_package_id = request.POST.get('delivery_package_id')  # Change this according to how you receive data
      
        
            # Insert DeliveryPackages if selected
            if delivery_package_id:
                #delivery_package = get_object_or_404(DeliveryPackages, id=delivery_package_id)
                delivery_package = DeliveryPackages.objects.filter(pk=delivery_package_id).first()

                order_item.delivery = delivery_package
                order_item.save()
                return redirect('app:all-menu')
            
            
        else:
        
                       


            # Assuming you get the selected DeliveryPackage and AddonGoods from form data or somewhere else
            delivery_package_id = request.POST.get('delivery_package_id')  # Change this according to how you receive data
            addon_ids = request.POST.getlist('addon_ids')  # Change this according to how you receive multiple addon IDs
         
            # Insert DeliveryPackages if selected
            if delivery_package_id and addon_ids:
                #delivery_package = get_object_or_404(DeliveryPackages, id=delivery_package_id)
                delivery_package = DeliveryPackages.objects.filter(pk=delivery_package_id).first()
                
                order_item.delivery = delivery_package
                order_item.save()
                addon_objects = AddonGoods.objects.filter(id__in=addon_ids)
                order_item.addon.set(addon_objects)
                
                '''for addon in addon_objects:
                    order_item.addon.add(addon)
                order_item.save()'''
                return redirect('app:all-menu')
            
        
            else:
                messages.info(request, "At least You Must Select Delivery Package and addon.")
                return redirect(request.META['HTTP_REFERER']) 

    context = {'addon': addon, 'delivery': delivery, 'order_item': order_item, 'goods': goods, 'food_details': food_details, 'selected_addons': selected_addons}        
    return render(request, templates_name, context)





'''
 

    
@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Good, pk=pk )    
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
    )
    order_item.quantity += 1
    order_item.save()
    return redirect("app:order-summary")

 '''   


@compress_page
@login_required
def add_to_wish(request, slug):
    item = get_object_or_404(Good, slug=slug)
    wish_item, created = WishList.objects.get_or_create(
        item=item,
        user=request.user,
    )
    if created:
        messages.info(request, "This item was added to your cart.")
        return redirect("web:order-summary")
    else:
        messages.info(request, "you have before item was added to your cart.")
        return redirect("web:order-summary")








@require_http_methods(['DELETE'])
@compress_page
@login_required
def minus_to_cart(request, pk):
    item = get_object_or_404(Good, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, paid=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        try:
            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity -= 1
                order_item.full_clean()
                order_item.save()
                #messages.info(request, "Item Has Been Minus to your cart")
                return redirect(request.META['HTTP_REFERER']) 
            else:
                order.items.add(order_item)
                #messages.info(request, "Item Has Been Minus from to your cart")
                return redirect(request.META['HTTP_REFERER']) 
    
        except ValidationError:
            #messages.info(request, "You Cannot Have Empty Value")
            return redirect(request.META['HTTP_REFERER']) 
            
            
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, ref_code = create_ref_code())
        order.items.add(order_item)
        return redirect(request.META['HTTP_REFERER']) 




@require_http_methods(['DELETE'])
@compress_page
@login_required
def minus_to_cart_plugin(request, pk, food_pk):
    item = get_object_or_404(PluginFoods, pk=pk)
    food = Good.objects.filter(pk=food_pk).first()

    order_item, created = PluginOrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False,
        foods = food
    )
    order_qs = OrderItem.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        try:
            if order.plugin.filter(item__pk=item.pk, foods__id=food.pk).exists():
                order_item.quantity -= 1
                order_item.full_clean()
                order_item.save()
                return redirect(request.META['HTTP_REFERER']) 
            else:
                order.plugin.add(order_item)
                return redirect(request.META['HTTP_REFERER']) 
    
        except ValidationError:
            return redirect(request.META['HTTP_REFERER']) 
            
            
    else:
        ordered_date = timezone.now()
        order = OrderItem.objects.create(user=request.user, ordered_date=ordered_date)
        order.plugin.add(order_item)
        return redirect(request.META['HTTP_REFERER']) 


@require_http_methods(['DELETE'])
@compress_page
@login_required
def remove_from_cart_plugin(request, pk, food_pk):
    item = get_object_or_404(PluginFoods, pk=pk)
    food = Good.objects.filter(pk=food_pk).first()
    
    order_qs = OrderItem.objects.filter(
        user=request.user,
        ordered = False,
        plugin__item__exact = item.pk
    )
    print(order_qs)
    if order_qs.exists():
        print("Hello World")
        order = order_qs[0]
        # check if the order item is in the order
        if order.plugin.filter(item__pk=item.pk, foods__id=food.pk).exists():
            
            order_item = PluginOrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
                foods_id = food.pk
                
            )[0]
            order.plugin.remove(order_item)
            order_item.delete()
            #messages.info(request, "Item Has Been Minus from to your cart")
            return redirect(request.META['HTTP_REFERER']) 
        else:
            #messages.info(request, "Item Has Been Minus from to your cart")
            return redirect(request.META['HTTP_REFERER']) 
    else:
        #messages.info(request, "Item Has Been Minus from to your cart")
        return redirect(request.META['HTTP_REFERER']) 



@require_http_methods(['DELETE'])
@compress_page
@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Good, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        paid=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            #messages.info(request, "Item Has Been Minus from to your cart")
            return redirect(request.META['HTTP_REFERER']) 
        else:
            #messages.info(request, "Item Has Been Minus from to your cart")
            return redirect(request.META['HTTP_REFERER']) 
    else:
        #messages.info(request, "Item Has Been Minus from to your cart")
        return redirect(request.META['HTTP_REFERER']) 





@login_required
def AllMenu(request):
    
    # Get items in the cart for the current user
    items_in_cart = OrderItem.objects.filter(user=request.user, ordered=False).order_by('created_at')

    # Get all available items not in the cart
    all_items = Good.objects.all()
    #.order_by('category') 
    
    categories = Category.objects.all()
    goods_by_category = {}

    for category in categories:
        goods_by_category[category] = Good.objects.filter(category=category, available=True)
        
        
    

    addon = AddonGoods.objects.all()
    items_not_in_cart = [item for item in all_items if item not in [cart_item.item for cart_item in items_in_cart]]

    packages = DeliveryPackages.objects.all()
    template_name = 'customer/allmenu.html'
    
    
   
    
    
    try:
        order = Order.objects.filter(user=request.user, paid=False).first()
    except Order.DoesNotExist:
        order = None
        
    food_details = []
    addon_food = []
    package_food = []
    allplugin_food = []
    total_package = Decimal(0)
    total_plugin = Decimal(0)
    
    for item in items_in_cart:
        
        if item.delivery is not None:
            #print(f'{item.item.name} | {item.delivery.name}')
            itemname = item.item.name
            deliveryname = item.delivery.name
            packageprice = item.delivery.price
            #total_package = sum(packageprice)
            total_package += packageprice
            package_food.append({
                'itemname': itemname,
                'deliveryname': deliveryname,
                'packageprice': packageprice
                
            })
    
        for addon in item.addon.all():
            addon =  addon.name
            itemname = item.item.name
            addon_food.append({
                'addon': addon,
                'itemname': itemname
            })  
            
         
        for plugins in item.plugin.all():
            #print(f'{plugins.foods} | {plugins.item} | {plugins.quantity}') 
            plugin_food = plugins.foods
            plugin_item = plugins.item
            plugins_quantity = plugins.quantity
            plugin_price = plugins.foods.price 
            total_plugin += plugins.foods.price * plugins.quantity
            #print(plugins_quantity)
            
            allplugin_food.append({
                'plugin_food': plugin_food,
                'plugin_item': plugin_item,
                'plugins_quantity': plugins_quantity,
                'plugin_price': plugin_price
                
            })  
        

    #print(total_package)                    
    #print(total_plugin)
    #print(addon_food) 
    #print(allplugin_food) 
    
    
    
    

    context = {'addon': addon, 'object': order, 'items_in_cart': items_in_cart, 'packages': packages, 
               'all_items': all_items, 'package_food': package_food, 'addon_food': addon_food, 
               'allplugin_food': allplugin_food, 'total_package': total_package,'total_plugin': total_plugin,
                'goods_by_category': goods_by_category, 'categories': categories}
    return render(request, template_name, context)



@login_required
def OrderSummaryView(request, get_total, total_plugin, total_package):
    
    get_total = float(get_total)
    total_plugin = float(total_plugin)
    total_package = float(total_package)
  
    
    
        

    distance = ''
   

    try:
        order = Order.objects.get(user=request.user, paid=False)
   
        for order_item in order.items.all():  
            pass
           
            if  order.shipping_address is not None:
                distance = gmaps.distance_matrix('Iya Oyo Amala, 112 Idris Gidado St, Wuye 900108, Ankuru, Federal Capital Territory', order.shipping_address)['rows'][0]['elements'][0]

    
    except Order.DoesNotExist:
        order = None
        distance = ()



    #vendor = OrderItem.objects.select_related('order').values('item__vendor__name').annotate(dcount=Count('item__vendor__name')).order_by()
    delivery = DeliveryDetails.objects.select_related('user').filter(user=request.user.pk)
    template_name = 'customer/ordersummary.html'
    form = CheckoutForm(instance=order)


    context = {'form': form, 'object': order, 'delivery': delivery,  'distance': distance, 'google_api_key': conf_settings.GOOGLE_API_KEY,
               'get_total': get_total, 'total_plugin': total_plugin, 'total_package': total_package}
 
    if request.method == 'POST' and 'BtnDelivery' in request.POST: 
        message = request.POST.get('message')
        address = request.POST.get('myaddress')
        location = request.POST.get('location')
        myLocation = Location.objects.get(pk=location)
       
        
        
        
        Order.objects.filter(user=request.user).update(shipping_address=address, ordernote=message, location=myLocation)
      
     
        messages.info(request, "The Address Has been Update")
        return redirect(request.META['HTTP_REFERER']) 



    if request.method=='POST' and 'BtnUpdate' in request.POST:
        form = CheckoutForm(request.POST or None, instance=order)

        if form.is_valid():
            #order = form.save()                
            order.save()
            messages.info(request, "The Detail have Been Updated")
            return redirect(request.META['HTTP_REFERER']) 
        

 


    return render(request, template_name, context)






@login_required
@compress_page
def OrderReceipt(request):
    order = Order.objects.get(user=request.user, paid=False)
    restaurant = OrderItem.objects.select_related('order').values('item__restaurant__name').annotate(dcount=Count('item__restaurant__name')).order_by()
    context = {'object': order, 'restaurant': restaurant}
    template_name = 'customer/receipt.html'
    return render(request, template_name, context)





@login_required
@compress_page
def SuccessPayment(request, pk):
    template_name = 'customer/receipt.html'
    order = get_object_or_404(Order, pk=pk)
    Order.objects.filter(pk=order.id).update(paid=True)
    restaurant = OrderItem.objects.select_related('order').values('item__restaurant__name').annotate(dcount=Count('item__restaurant__name')).order_by()
    context = {'object': order, 'restaurant': restaurant}
    return render(request, template_name, context)





@login_required
@compress_page
def verifyPayment(request, paid_amount, mins, distance, delivery_amount, food_amount, tax_amount, package_amount):
    
    
    txref = request.GET['ref'].strip()
    paid_amount = paid_amount
    mins = mins
    distance = distance
    delivery_amount = delivery_amount
    food_amount = food_amount
    tax_amount = tax_amount
    package_amount = package_amount
    
    

    if Order.objects.filter(ref_code__iexact=txref, paid=True).exists():
        messages.info(request, "This Order is under Process, Please, kindly wait to hear from us.")
        return redirect('/customer/myorder') 
    
        

    plugins = PluginOrderItem.objects.filter(ordered=False, user=request.user)
   
    for plugin in plugins:
        plugin.ordered = True
        plugin.save()
            
            
    invoice = get_object_or_404(Order, ref_code__iexact=txref)
    order_items = invoice.items.all()
    order_items.update(ordered=True)
    for item in order_items:
        item.save()

    try:
        invoice = get_object_or_404(Order, ref_code__iexact=txref)
       
    except Exception as e:
        raise Http404("Invalid Invoice PIN")
    
    
    
    Order.objects.filter(ref_code__iexact=txref).update(paid=True, mins=mins, distance=distance, paid_amount=paid_amount, 
                                                        delivery_amount=delivery_amount, food_amount=food_amount, tax_amount=tax_amount, 
                                                        package_amount=package_amount)





    to = invoice.phone_number

    message_details = f'Hi {invoice.user.username}!  The Food Package you ordered for is on the way. Ensure someone is available to pick it.'
    message = httpx.get(f"https://www.bulksmsnigeria.com/api/v1/sms/create?api_token={sms_api}&to={to}&body={message_details}")
    url = "https://api.paystack.co/transaction/verify/" + txref
    response = httpx.get(url, 
            headers={'Authorization': 'Bearer ' + SECKEY})
    json_response = response.json()
 
    if json_response['status'] == True:
              
        if json_response['data']['status'] == 'success' and json_response['data']['currency'] == 'NGN' and json_response['data']['reference'] == txref:
            #json_response['data']['amount'] == ( amount * 100) and \
            return render(request, 'customer/receipt.html', {'invoice': invoice, 'response' :json_response, 'amount': paid_amount})

    return HttpResponseRedirect(reverse('payTnvoice', args=[invoice.ref_code]))




#The is The Function for Making Pyament on dlivery
@login_required
@compress_page
def PayOnDelivery(request, pk, amount, mins, distance, receiver_code):
    amount = amount
    mins = mins
    distance = distance

    invoice = get_object_or_404(ReceiverDetails, receiver_code__iexact=receiver_code)

    if invoice.process == True:
        messages.info(request, "This Package is under Process, Please, kindly wait to hear from us.")
        return redirect('/customer/myorder#parcel') 

    ReceiverDetails.objects.filter(receiver_code__iexact=receiver_code).update(process=True)
    to = invoice.r_telephone
    PackageDetails.objects.filter(pk=pk).update(mins=mins, distance=distance, paid_amount=amount, pay_on_delivery=True, tracking_number=random_string())
    package =  PackageDetails.objects.get(pk=pk)
    mynumber= package.tracking_number
    message_details = f'Hi {invoice.fullname}! {mynumber} You Have a Package of {package.nature_of_goods} from {invoice.sender.get_full_name()} with on its way. Thanks!'
    message = httpx.get(f"https://www.bulksmsnigeria.com/api/v1/sms/create?api_token={sms_api}&to={to}&body={message_details}")
    return render(request, 'customer/packagereceipt.html', {'invoice': invoice,  'package': package})







@login_required
@compress_page
def verifyPaymentPackage(request, pk, amount, mins, distance):
    txref = request.GET['ref'].strip()
    amount = amount
    mins = mins
    distance = distance

    try:
        invoice = get_object_or_404(ReceiverDetails, receiver_code__iexact=txref)
        

    except Exception as e:
        raise Http404("Invalid Invoice PIN")
    

    if invoice.process == True:
        messages.info(request, "This Package is under Process, Please, kindly wait to hear from us.")
        return redirect('/customer/myorder#parcel')
    
    ReceiverDetails.objects.filter(receiver_code__iexact=txref).update(process=True)

    to = invoice.r_telephone
    PackageDetails.objects.filter(pk=pk).update(paid=True, mins=mins, distance=distance, paid_amount=amount, tracking_number=random_string())
    package =  PackageDetails.objects.get(pk=pk)
    mynuber= package.tracking_number
    message_details = f'Hi {invoice.fullname}! {mynuber} You Have a Package of {package.nature_of_goods} from {invoice.sender.get_full_name()} with on its way. Ensure someone is available to pick it. Thanks!'
    message = httpx.get(f"https://www.bulksmsnigeria.com/api/v1/sms/create?api_token={sms_api}&to={to}&body={message_details}")


    url = "https://api.paystack.co/transaction/verify/" + txref
    response = httpx.get(url, 
            headers={'Authorization': 'Bearer ' + SECKEY})
    json_response = response.json()
    #confirm that the response for the transaction is su
    if json_response['status'] == True:
              
        if json_response['data']['status'] == 'success' and json_response['data']['currency'] == 'NGN' and json_response['data']['reference'] == txref:
            #json_response['data']['amount'] == ( amount * 100) and \
            #restaurant = OrderItem.objects.select_related('invoice').values('item__vendor__name', 'item__vendor__fulladdress').annotate(dcount=Count('item__vendor__name')).order_by()
            invoice_word = num2words(amount)
            return render(request, 'customer/packagereceipt.html', {'invoice': invoice, 'invoice_word': invoice_word, 'package': package, 'response' :json_response})

    return HttpResponseRedirect(reverse('payTnvoice', args=[invoice.receiver_code]))




'''
class SearchRestaurants(ListView):
    model = Vendor
    context_object_name = "restaurant"
    template_name = "customer/search.html"
    

    def get_queryset(self):
        query = self.request.GET.get("city") 
        query2 = self.request.GET.get("location")
        vendors = Vendor.objects.filter(Q(city__pk=query) & Q(location__pk=query2))
        return vendors
'''
    

@compress_page
@login_required
def MyOrder(request):
    template_name = 'customer/myorder.html'
    order = Order.objects.filter(user=request.user)
    parcel = PackageDetails.objects.filter(user=request.user).select_related('receiver_details').order_by('-created_at')
    address = DeliveryDetails.objects.filter(user=request.user)
    passform = PasswordChangeForm(request.user or None)
    userForm = UserChangeForm(request.POST or None, instance=request.user)
    
   
    if 'myProfile' in request.POST:
        if userForm.is_valid() and form.is_valid():
            userForm.save()
            form.save()
            messages.success(request, "The User Profile Has Been Updated")
            return redirect("app:my-order")
        
        
    if 'myPassword' in request.POST:
        if passform.is_valid():
            passform.save()
            passform.save()
            messages.success(request, "The User Profile Has been Changes Successfully")
            return redirect("app:my-order")
        
        
        
    '''if request.method=='POST':
        order.update(ref_code=create_ref_code(), paid=False, being_delivered=False)
        messages.info(request, "You Are Re-Ordering This Packgae")
        return redirect("customer:order-summary")'''
    context = {'object': order, 'parcel': parcel, 'address': address, 'passform': passform, 'userForm': userForm}
    return render(request, template_name, context)


@login_required
def MyAddress(request):
    template_name = 'customer/address.html'
    delivery = DeliveryDetails.objects.select_related('user').filter(user=request.user.pk)
    form = DetailsForm()
    order = Order.objects.filter(user=request.user).filter(paid=False)

    if request.method=='POST':
        form = DetailsForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user                
            order.save()
            messages.info(request, "New Address Has been Added")
            return redirect("customer:order-summary") 
    context = {'object': order, 'delivery': delivery, 'form': form}
    return render(request, template_name, context)



@login_required
def closePayment(request):
    #order = get_object_or_404(Order, user=request.user, paid=False)
    mycode = create_ref_code()
    Order.objects.filter(user=request.user, paid=False).update(ref_code=mycode)
    qr_image = qrcode.make(mycode)
    qr_offset = Image.new('RGB', (310, 310), 'white')
    draw_img = ImageDraw.Draw(qr_offset)
    qr_offset.paste(qr_image)
    file_name = f'{mycode}-{request.user.username}qr.png'
    
    stream = BytesIO()
    qr_offset.save(stream, 'PNG')
    myorder = Order.objects.filter(user=request.user, ref_code=mycode).first()
    myorder.qr_image.save(file_name, File(stream), save=False)
    qr_offset.close()
    myorder.save()
        
    
    messages.info(request, "The Payment Failed or You Cancled The Process")
    return redirect(request.META['HTTP_REFERER']) 




@compress_page
@login_required
def ParcelMessage(request):
    template_name = 'customer/parcel.html'
    form = ReceiverDetailsForm()
    if request.method=='POST':
        form = ReceiverDetailsForm(request.POST or None, request.FILES or None,)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.sender  = request.user
            parcel.save()
            messages.info(request, "The Receiver Data Have been updated Successfully")
            return redirect('customer:parcel-package', parcel.pk)
       
    context = {'form': form}
    return render(request, template_name, context)


@compress_page
@login_required
def ParcelPackageDetails(request, pk):
    template_name = 'customer/package.html'
    parcel = get_object_or_404(ReceiverDetails, pk=pk)
    myparcel = ReceiverDetails.objects.get(pk=parcel.pk, sender=request.user)
    distance = gmaps.distance_matrix(myparcel.picking_address, myparcel.deliver_address)['rows'][0]['elements'][0]
    form = PackageDetailsForm()

    try:
        details = PackageDetails.objects.filter(receiver_details__receiver_code=myparcel.receiver_code, receiver_details__process=False).first()
        #print(details.pk)
        if ReceiverDetails.objects.filter(pk=pk).exists() and details == True:
            messages.info(request, "The Parcel Information has been saved before Now, You can make Payment now")
            return redirect('customer:edit-parcel-package-message', parcel.pk, details.pk)
       
    except ReceiverDetails.DoesNotExist:
        pass


    

   
    if parcel.process == True:
        messages.info(request, "The Parcel Information has been saved, You can make Payment now")
        return redirect('customer:parcel-message')
    


    form = PackageDetailsForm(request.POST or None, request.FILES or None)
    if request.method=='POST':
        form = PackageDetailsForm(request.POST or None, request.FILES or None,)
        if form.is_valid():
            package = form.save(commit=False)
            package.receiver_details = myparcel
            package.user = request.user
            package.save()
            messages.info(request, "The Parcel Information has been saved, You can make Payment now")
            #return redirect(request.META['HTTP_REFERER']) 
            return redirect('customer:payment-parcel-package', parcel.pk, package.pk)
  

    
    context = {'form': form, 'distance': distance, 'myparcel': myparcel}
    return render(request, template_name, context)

    





@compress_page
@login_required
def PackagePayment(request, pk, id):
    template_name = 'customer/packagepayment.html'
    package = get_object_or_404(ReceiverDetails, pk=pk)
    details = PackageDetails.objects.get(pk=id)
    
    if PackageDetails.objects.filter(pk=id, receiver_details__process=True).exists():
        package = PackageDetails.objects.filter(pk=id, receiver_details__process=True).first()
        return redirect('customer:final-receipt', package.pk)
    
    
    distance = gmaps.distance_matrix(package.picking_address, package.deliver_address)['rows'][0]['elements'][0]
    context = {'distance': distance, 'package': package, 'details': details}
    return render(request, template_name, context)






@compress_page
@login_required
def EditParcelMessage(request, pk, id):
    parcel = get_object_or_404(ReceiverDetails, pk=pk)
    template_name = 'customer/editparcel.html'
    distance = gmaps.distance_matrix(parcel.picking_address, parcel.deliver_address)['rows'][0]['elements'][0]

       
    if ReceiverDetails.objects.filter(pk=id, process=True).exists():
        parcel = ReceiverDetails.objects.filter(pk=id, process=True).first()
        return redirect('customer:parcel-package', parcel.pk)
       


    form = ReceiverDetailsForm(instance=parcel)
    if request.method=='POST':
        form = ReceiverDetailsForm(request.POST or None, request.FILES or None, instance=parcel)
        if form.is_valid():
            parcel = form.save()
            parcel.save()
            messages.info(request, "The Receiver Data Have been Successfully Updated")
            return redirect('customer:payment-parcel-package', parcel.pk, id)
            #return redirect(request.META['HTTP_REFERER']) 
            
       
    context = {'form': form, 'distance': distance, 'parcel': parcel}
    return render(request, template_name, context)



@compress_page
@login_required
def EditParcelPackageDetails(request, pk, id):
    package = get_object_or_404(PackageDetails, pk=id)

    template_name = 'customer/editpackage.html'
    distance = gmaps.distance_matrix(package.receiver_details.picking_address, package.receiver_details.deliver_address)['rows'][0]['elements'][0]


       
    if PackageDetails.objects.filter(pk=id, receiver_details__process=True).exists():
        package = PackageDetails.objects.filter(pk=id, receiver_details__process=True).first()
        messages.info(request, "The Parcel Is On Process You  Cannot Edit")
        return redirect('customer:final-receipt', package.pk)
    
 


    form = PackageDetailsForm(instance=package)

    if request.method=='POST':
        form = PackageDetailsForm(request.POST or None, request.FILES or None, instance=package)
        if form.is_valid():
            package = form.save()
            package.save()
            messages.info(request, "The Receiver Data Have been Successfully Updated")
            return redirect('customer:payment-parcel-package', pk, package.id)
            #return redirect(request.META['HTTP_REFERER']) 
            
       
    context = {'form': form, 'distance': distance, 'package': package}
    return render(request, template_name, context)



@compress_page
@login_required
def DeletPackage(request, pk, id):
    package = get_object_or_404(PackageDetails, pk=pk)
    PackageDetails.objects.get(pk=pk).delete()
    ReceiverDetails.objects.get(pk=id).delete()
    messages.info(request, "The Data Has Been Deleted Succesfull!")
    return redirect('/customer/myorder#parcel')


@compress_page
@login_required
def FinalPackageReceipt(request, pk):
    package = get_object_or_404(PackageDetails, pk=pk)
    return render(request, 'customer/packagereceiptfinal.html', {'package': package})



@compress_page
@login_required
def FinalOrdergeReceipt(request, pk):
    invoice = get_object_or_404(Order, pk=pk)
    return render(request, 'customer/orderereceiptfinal.html', {'invoice': invoice})



@compress_page
@login_required
def PosPrinting(request, pk):
    invoice = get_object_or_404(Order, pk=pk)
    return render(request, 'customer/posprinter.html', {'invoice': invoice})

@compress_page
@login_required
def closePackagePayment(request, pk):
    package = get_object_or_404(ReceiverDetails, pk=pk)
  
    ReceiverDetails.objects.filter(pk=package.pk).update(receiver_code=create_ref_code())
    messages.info(request, "The Payment Failed or You Cancled The Process")
    return redirect(request.META['HTTP_REFERER']) 


   


@compress_page
@login_required
def DeleteAddress(request, id):
    DeliveryDetails.objects.filter(id=id).delete()
    messages.info(request, "The Address Has Been Deleted Successfully!")
    return redirect(request.META['HTTP_REFERER']) 


@compress_page
@login_required
def EditAddress(request, id):
    
    address = get_object_or_404(DeliveryDetails, pk=id)
    template_name = 'customer/address.html'
 
    form = DetailsForm(instance=address)
    order = Order.objects.filter(user=request.user).filter(paid=False)

    if request.method=='POST':
        form = DetailsForm(request.POST, instance=address)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user                
            order.save()
            messages.info(request, "New Address has been Edited")
            return redirect("customer:order-summary") 
    context = {'object': order,  'form': form}
    return render(request, template_name, context)
    
    messages.info(request, "The Address Has Been Edit Successfully!")
    return redirect(request.META['HTTP_REFERER']) 



@compress_page
@login_required
def ChangePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_logout')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'customer/changepassword.html', {
        'form': form
    })


@compress_page
@login_required
def CustomerProfileUpdate(request, username):
    user = get_object_or_404(User, username=username)
   
    userform = UserChangeForm(instance=request.user) 
   

    if request.method == 'POST':
       
        uploaduser = UserChangeForm(request.POST, instance=request.user)
       
        
        if uploaduser.is_valid():
                uploaduser.save()
               
                messages.success(request, "Your Profile Has been uploaded Sucessfuly")
                return redirect('customer:my-order')
        else:
               
                userform = UserChangeForm(instance=request.user)
       


    return render(request, 'customer/customerprofile.html', { 'userform': userform})



@login_required
@customer_required
def SubscriptionPackageDetails(request, pk):
    package = get_object_or_404(SubscriptionPackage, pk=pk)
    return render(request, 'customer/packagedetails.html', {'package':package})









@login_required
@compress_page
def verifyPaymentOrderSubscription(request, amount, mins, distance):
    txref = request.GET['ref'].strip()
    amount = amount
    mins = mins
    distance = distance
 
    subscriber = Subscriber.objects.filter(user=request.user).first()
    new_usage = float(distance) + round(subscriber.usage, 2)


   
    if Order.objects.filter(ref_code__iexact=txref, paid=True).exists():
        messages.info(request, "This Order is under Process, Please, kindly wait to hear from us.")
        return redirect('/customer/myorder') 
    


    try:
        invoice = get_object_or_404(Order, ref_code__iexact=txref)
       
    except Exception as e:
        raise Http404("Invalid Invoice PIN")
    
    Order.objects.filter(ref_code__iexact=txref).update(paid=True, subscription=True, mins=mins, distance=distance, paid_amount=amount)

    Subscriber.objects.filter(user=request.user).update(usage=new_usage)

    to = invoice.user.profilecustomer.phone_number

    message_details = f'Hi {invoice.user.get_full_name()}!  The Food Package you ordered for is on the way. Ensure someone is available to pick it.'
    message = httpx.get(f"https://www.bulksmsnigeria.com/api/v1/sms/create?api_token={sms_api}&to={to}&body={message_details}")

    url = "https://api.paystack.co/transaction/verify/" + txref
    response = httpx.get(url, 
            headers={'Authorization': 'Bearer ' + SECKEY})
    json_response = response.json()
 
    if json_response['status'] == True:
              
        if json_response['data']['status'] == 'success' and json_response['data']['currency'] == 'NGN' and json_response['data']['reference'] == txref:
            #json_response['data']['amount'] == ( amount * 100) and \
            return render(request, 'customer/receipt.html', {'invoice': invoice, 'response' :json_response, 'amount': amount})

    return HttpResponseRedirect(reverse('payTnvoice', args=[invoice.ref_code]))
   




@login_required
@compress_page
def verifyPaymentPackageSubscription(request, pk, distance, code):
    txref = code
    distance = distance
    #print(distance)
   

    try:
        invoice = get_object_or_404(ReceiverDetails, receiver_code__iexact=txref)
        

    except Exception as e:
        raise Http404("Invalid Invoice PIN")
    

    if invoice.process == True:
        messages.info(request, "This Package is under Process, Please, kindly wait to hear from us.")
        return redirect('/customer/myorder#parcel')
    

    subscriber = Subscriber.objects.filter(user=request.user).first()
    #print(round(subscriber.usage, 2))
    new_usage = float(distance) + round(subscriber.usage, 2)
    Subscriber.objects.filter(user=request.user).update(usage=new_usage)
    
    ReceiverDetails.objects.filter(receiver_code__iexact=txref).update(process=True)
    to = invoice.r_telephone
    PackageDetails.objects.filter(pk=pk).update(paid=True, subscription=True, distance=distance, tracking_number=random_string())
    package =  PackageDetails.objects.get(pk=pk)
    mynumber= package.tracking_number
    message_details = f'Hi {invoice.fullname}! {mynumber} You Have a Package of {package.nature_of_goods} from {invoice.sender.get_full_name()} with on its way. Ensure someone is available to pick it. Thanks!'
    message = httpx.get(f"https://www.bulksmsnigeria.com/api/v1/sms/create?api_token={sms_api}&to={to}&body={message_details}")

    return render(request, 'customer/packagereceipt.html', {'invoice': invoice, 'package': package})

   



def CheckSubscription(request):
    subscribers = Subscriber.objects.filter()
    for subscriber in subscribers:
        if  subscriber.usage > subscriber.package.distance:
            subscribers.update(active=False)
            #return redirect('customer:my-order')
    return render(request, 'frontpage/index.html')


'''

@login_required
def MerchantDetails(request, username):
    user = get_object_or_404(CustomUser, username=username)
    profile = MerchantProfile.objects.filter(user=user).first()
    userform = UserChangeForm(instance=request.user) 
    upload = MerchantProfileForm(instance=profile)

    if request.method == 'POST':
        upload = MerchantProfileForm(request.POST, request.FILES, instance=profile)
        uploaduser = UserChangeForm(request.POST, instance=request.user)
        customer_referral_code = request.POST['customer_referral_code']
        check = CustomUser.objects.filter(referral_code=customer_referral_code).exists()
        check_user = CustomUser.objects.filter(referral_code=request.user.referral_code).first() 
        if check == True and customer_referral_code != check_user:
            if upload.is_valid() and uploaduser.is_valid():
                uploaduser.save()
                u = upload.save(commit=False)
                u.customer_referral_code = customer_referral_code
                u.save()
                messages.success(request, "Your Profile Has been uploaded Sucessfuly")
                return redirect('web:merchant-dashboard')

            else:
                upload = MerchantProfileForm(instance=profile)
                userform = UserChangeForm(instance=request.user)
        else:
            if upload.is_valid() and uploaduser.is_valid():
                uploaduser.save()
                u = upload.save(commit=False)
                u.customer_referral_code = ''
                u.save()
                messages.success(request, "Your Profile Has been uploaded Sucessfuly")

                return redirect('web:merchant-dashboard')
            else:
                upload = MerchantProfileForm(instance=profile)
                userform = UserChangeForm(instance=request.user)


    return render(request, 'merchant/merchantprofile.html', {'form':upload, 'userform': userform})


def BuyerDetails(request, username):
    user = get_object_or_404(CustomUser, username=username)

  


    profile = IndividualProfile.objects.filter(user=user).first()
    

    upload = IndividualProfileForm(instance=profile)
    user = UserChangeForm()

  
    if request.method == 'POST':
        upload = IndividualProfileForm(request.POST, request.FILES, instance=profile)
        if upload.is_valid():
            upload.save()
            return redirect('web:individual-dashboard')
    else:
        upload = IndividualProfileForm(instance=profile)
        userform = UserChangeForm()

    return render(request, 'individualprofile.html', {'form':upload, 'userform': userform})




def ChangePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'merchant/change_password.html', {
        'form': form
    })




# importing googlemaps module
import googlemaps
  
origin_latitude = 12.9551779
origin_longitude = 77.6910334
destination_latitude = 28.505278
destination_longitude = 77.327774
distance = gmaps.distance_matrix([str(origin_latitude) + " " + str(origin_longitude)], [str(destination_latitude) + " " + str(destination_longitude)], mode='walking')['rows'][0]['elements'][0]
print(distance)



def CategoryFood(request, pk):
    template_name = 'customer/categoryfood.html'
    category = get_object_or_404(Category, pk=pk)
    menu = SubCategory.objects.select_related('category').all()
    print(menu)
    context = {'menu': menu}
    return render(request, template_name, context)



@customer_required
def PlaceOrder(request):
    template_name = 'customer/placeorder.html'
    user = request.user
    orderuser = User.objects.get(id=request.user.id)
    name = request.session.get('name')
    form = SubCategoryFormset()

    if request.method == 'GET':
        for formset in form:
            formset.fields['name'] = forms.ModelChoiceField(SubCategory.objects.filter(category=name))
    
    elif request.method == 'POST':  
        formorder = OrderCreateForm(request.POST)
        formset = SubCategoryFormset(request.POST) 

        if formorder.is_valid() and formset.is_valid():
            order = formorder.save(commit=False)
            order.ref_code = create_ref_code()
            order.user = user
            #order.user = orderuser
            order.save()

                
            for form in formset:
                sub = form.cleaned_data.get('name')
                quantity = form.cleaned_data.get('quantity')
                subcategory = SubCategory.objects.get(id=sub)
                
                if subcategory:
                    ProcessOrder(subcategory=subcategory, order=order, user=user, quantity=quantity).save()
                    
            return redirect('customer:billing', order.id)
            

         
    context = {'form': form}

    
   
    return render(request, template_name, context)

@customer_required
def MyBilling(request, pk):
    template_name = 'customer/order.html'
    order = get_object_or_404(Order, pk=pk, paid=False)  
    item = order.order.all() 
    total_prices = sum((items.subcategory.price * items.quantity) for items in item)
    form = CheckoutForm()
    context = {'form': form, 'order': order, 'total_prices': total_prices,}
    if request.method == 'POST':  
        form = CheckoutForm(request.POST, instance=order)
        if form.is_valid():
            package = form.cleaned_data.get('package')
            shipping_address = form.cleaned_data.get('shipping_address')
            ordernote = form.cleaned_data.get('ordernote')
            pck = PackageType.objects.get(id=package.id)
            grand_total_price = total_prices + pck.price
            order = form.save(commit=False)                
            order.shipping_address = shipping_address
            order.ordernote = ordernote
            order.package = pck
            order.total_price = grand_total_price
            order.save()

            return redirect('customer:payment', order.id)

    return render(request, template_name, context)
        
@customer_required
def PaymentProcess(request, pk):
    order = get_object_or_404(Order, id=pk, paid=False)

    print(order.total_price)
    templates_name = 'customer/payment.html'
    return render(request, templates_name, {'order': order})

 

@customer_required
def SuccessPayment(request, pk):

    order = get_object_or_404(Order, pk=pk)

    Order.objects.filter(pk=order.id).update(paid=True)
    return render(request, 'customer/successpayment.html')

@customer_required
def HistoryOrder(request, pk):
    template_name = 'customer/orderhistory.html'
    order = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, template_name, {'order': order},)







@customer_required
def InfoEdit(request,pk):
    template_name = 'customer/editorderinfo.html'
    order = get_object_or_404(Order, pk=pk, paid=False)
    item = order.order.all() 
    total_prices = sum((items.subcategory.price * items.quantity) for items in item)
    #print(total_prices)
    
    form = CheckoutForm(request.POST or None, instance=order)
    if request.method == 'POST':
        if form.is_valid():
            package = form.cleaned_data.get('package')
            pck = PackageType.objects.get(id=package.id)
            p = form.save(commit=False)
            p.total_price  = pck.price + total_prices
            p.save()
            return redirect('customer:payment', order.id)
    return render(request, template_name, {'form': form})



'''


    
    
    


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'customer/password_change_form.html'
    #success_url = reverse_lazy('password_change_done')


    def get_success_url(self):
        messages.success(self.request, 'Your Password Has Successful Changed')
        return reverse_lazy('app:my-order')
    
    
    

'''
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'customer/user_update.html'
    #success_url = reverse_lazy('profile')  # Update with the URL for the user profile page

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
            messages.success(self.request, 'Your Data Has Been Successful Changed')
        return reverse_lazy('app:my-order')
        
'''


@login_required 
def UserProfileUpdateView(request):


    template_name = 'customer/user_update.html' 
    userForm = UserChangeForm(request.POST or None, instance=request.user)
    form = CustomerProfileForm(instance=request.user.profile)
   
    if request.method == 'POST':
        if userForm.is_valid() and form.is_valid():
            userForm.save()
            form.save()
            messages.success(request, "The User Has been Add to A Group")
            return redirect("app:user-dashboard")
            
      
   
    return render(request, template_name, {'userForm': userForm, 'form': form,})
    
    
    
    

@login_required
def UpdatePackages(request):
    order = Order.objects.get(user=request.user, paid=False)
    
    #if request.method == 'POST':
    if 'addPackages' in request.POST:
        #selected_package_name = form.cleaned_data['name']
        selected_package_name = request.POST.get('selected_package_name')
        print(selected_package_name)
        selected_package = DeliveryPackages.objects.get(pk=selected_package_name.pk)
        order.deliveryPackages = selected_package
        order.save()
        messages.info(request, "Item Has Been Minus from to your cart")
        return redirect(request.META['HTTP_REFERER']) 
    
    return redirect(request.META['HTTP_REFERER'])
