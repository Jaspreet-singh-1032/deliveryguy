from django.contrib import admin
from app.models import *
from django.db.models import Count

# Register your models here.
admin.site.register(User)
admin.site.register(ProfileBike)
admin.site.register(ProfileCustomer)
admin.site.register(Category)
#admin.site.register(Order)
admin.site.register(OrderItem)
#admin.site.register(Good)




admin.site.register(DeliveryDetails)
admin.site.register(Settings)
admin.site.register(PackageDetails)
admin.site.register(ReceiverDetails)
admin.site.register(Location)
admin.site.register(Subscriber)
admin.site.register(SubscriptionPackage)
admin.site.register(LoginAdvert)
admin.site.register(HomeAdvert)
admin.site.register(DeliveryPackages)
admin.site.register(OpenHours)
admin.site.register(BlogPost)
admin.site.register(BlogCategory)
admin.site.register(PluginOrderItem)
admin.site.register(PluginFoods)






class LocationPaidAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'paid', 'schedule', 'created_at']
    list_filter = ['location', 'paid']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Customize the queryset to include count per location and payment status
        extra_context['location_paid_count'] = Order.objects.values('location', 'paid').annotate(count=Count('id')).order_by('location', 'paid')
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Order, LocationPaidAdmin)
admin.site.register(AddonGoods)



class GoodImageGalleryInline(admin.TabularInline):
    model = GoodImageGallery
    extra = 1  # Number of empty forms to display
    
    


class GoodAdmin(admin.ModelAdmin):
    inlines = [GoodImageGalleryInline]

admin.site.register(Good, GoodAdmin)

'''

from django.contrib import admin
from app.models import *
from django.apps import apps

models = apps.get_models()

print(models)



for model in models:
    admin.site.register(model)




'''
