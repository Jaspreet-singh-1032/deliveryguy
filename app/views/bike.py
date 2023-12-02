from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.contrib.auth.forms import PasswordChangeForm
from ..decorators import bike_required
from ..forms import *
from ..models import *
from django.contrib.messages.views import SuccessMessageMixin





@bike_required
def BikeDashboard(request):
    new_order = Order.objects.filter(paid=True, taken=False)
    
    new_message = PackageDetails.objects.filter(paid=True, taken=False)
    ongoingmessage = PackageDetails.objects.filter(bike=request.user, ongoing=True).first()
    ongoinorder = Order.objects.filter(bike=request.user, ongoing=True).first()




    

    context = {'new_order': new_order, 'new_message': new_message, 'ongoingmessage': ongoingmessage, 'ongoinorder': ongoinorder}
    return render(request, 'bike/dashboard.html', context)




class BikeSignUpView(CreateView):
    model = User
    form_class = BikeSignUpForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'bikeman'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        p = ProfileBike.objects.get(user=self.request.user.id)
        return redirect('bike:bike_profile', p.id)

@bike_required
def BikeProfile(request, pk):
    template_name = 'bike/bikeprofile.html'
    bike = get_object_or_404(ProfileBike, pk=pk)
    form = BikeProfileForm(request.POST or None, request.FILES or None, instance = bike)
    if request.method == 'POST':
        if form.is_valid():
            p = form.save(commit=False)
            p.save()
            return redirect('bike:dashboard')
    return render(request, template_name, {'form': form})

@bike_required
def DeliveryOrder(request):
    template_name = 'bike/orderhistory.html'
    order = Order.objects.filter(received=False, paid=True).order_by('-created_at')

    
    
    return render(request, template_name, {'order': order})


@bike_required
def DetailsOrder(request, pk):
    template_name = 'bike/orders.html'
    orders = get_object_or_404(Order, pk=pk)
    neworder = orders.id
    order = ProcessOrder.objects.filter(order=orders).first()
    if request.method == 'POST':
       
        p = Order.objects.filter(id=neworder).update(received=True)
        return redirect('bike:accept_order', orders.id)

    return render(request, template_name, {'orders': orders, 'order': order})

@bike_required
def AcceptOrder(request, pk):
    template_name = 'bike/accept.html'
    orders = get_object_or_404(Order, pk=pk)
    neworder = orders.id
    order = ProcessOrder.objects.filter(order=orders).first()
    if request.method == 'POST':
        p = Order.objects.filter(id=neworder).update(shipped=True)
        return redirect('bike:complete_order', orders.id)
    return render(request, template_name, {'orders': orders, 'order': order})


@bike_required
def AcceptPackage(request, pk):
    #template_name = 'bike/acceptmessage.html'
    message = get_object_or_404(PackageDetails, pk=pk)
    PackageDetails.objects.filter(pk=message.pk).update(taken=True, ongoing=True, bike=request.user)
    messages.info(request, "You have Picked the Order, You May Not be able to See New Order Until You Finish This")
    return redirect('bike:message-ongoing', message.id)
  

@bike_required
def AcceptOrder(request, pk):
    #template_name = 'bike/acceptmessage.html'
    message = get_object_or_404(Order, pk=pk)
    Order.objects.filter(pk=message.pk).update(taken=True, ongoing=True, bike=request.user)
    messages.info(request, "You have Picked the Order, You May Not be able to See New Order Until You Finish This")
    return redirect('bike:order-ongoing', message.id)
  



@bike_required
def OnGoingPackage(request, pk):
    template_name = 'bike/ongoingmessage.html'
    message = get_object_or_404(PackageDetails, pk=pk)
    context = {'message': message}
    return render(request, template_name, context)




@bike_required
def OnGoingOrder(request, pk):
    template_name = 'bike/ongoingmessage.html'
    message = get_object_or_404(PackageDetails, pk=pk)
    context = {'message': message}
    return render(request, template_name, context)



@bike_required
def CompleteOrder(request, pk):
    message = get_object_or_404(PackageDetails, pk=pk)
    PackageDetails.objects.filter(pk=message.pk).update(being_delivered=True,  ongoing=False,  bike=request.user)
    messages.info(request, "You Completed The Order, You can Pick Another Nearest Other Now")
    return redirect('bike:dashboard')
  


@bike_required
def CancelOrder(request, pk):
    message = get_object_or_404(PackageDetails, pk=pk)
    PackageDetails.objects.filter(pk=message.pk).update(taken=False, ongoing=False, bike='')
    messages.info(request, "You Have Cancelled The Other, Someone Else will Pick it")
    return redirect('bike:dashboard')



@bike_required
def OnGoingPackageDetails(request, pk):
    template_name = 'bike/ongoingmessage.html'
    message = get_object_or_404(PackageDetails, pk=pk)
    context = {'message': message}
    return render(request, template_name, context)