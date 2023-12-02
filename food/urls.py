"""food URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from app.views import general, customer, bike
from  django.contrib.auth import login
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views







urlpatterns = [
    path('', include('app.urls')),
    #path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    #path('apiv1/', include('apiV1.urls')),
    #path('apiv2/', include('appV2.urls')),
    path('admin/', admin.site.urls),
    path('accounts/signup/customer/', customer.CustomerSignUpView.as_view(), name='customer_signup'),
    path('accounts/signup/bike/', bike.BikeSignUpView.as_view(), name='bike_signup'),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
       auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    #path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    
    
    path('accounts/', include('allauth.urls')),
    

    

]

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

admin.site.site_header = "DeliveryGuy Admin"
admin.site.site_title = "DeliveryGuy Admin Portal"
admin.site.index_title = "Welcome to Delivery Admin Portal"





if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = "food.exception.handler404"

handler500 = "food.exception.handler500"








