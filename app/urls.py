from django.urls import include, path
from .views import general, customer, bike

urlpatterns = [

    path('', general.FrontPage, name='front_page'),
    
    path('logout', general.logout_user, name='user_logout'),
    path("login", general.login, name='userlogin'),
    path('vendorbytype/<name>/', general.AllVendor, name='all-vendors-type'),
    path('blogdetails/<slug>/', general.BlogDetails, name='post-detail'),
    
    


    path('bike/', include(([

        path('dashboard', bike.BikeDashboard, name='dashboard'),
        path('profile/<pk>', bike.BikeProfile, name='bike_profile'),
        path('orders', bike.DeliveryOrder, name='order_delivery'),
        path('ordersdetails/<pk>', bike.DetailsOrder, name='details'),
        path('orderaccept/<pk>', bike.AcceptOrder, name='accept-order'),
        path('ongoingmessage/<pk>/', bike.OnGoingOrder, name='order-ongoing'),
        
        
        path('packagecompleted/<pk>', bike.CompleteOrder, name='package-complete'),
        path('cancelpackage/<pk>', bike.CancelOrder, name='cancel-package'),
        
        path('messageaccept/<pk>/', bike.AcceptPackage, name='accept-message'),
        path('ongoingmessage/<pk>/', bike.OnGoingPackage, name='message-ongoing'),
        path('ongoingmessagedetails/<pk>/', bike.OnGoingPackageDetails, name='message-ongoing-details'),

      


   
      
    ], 'app'), namespace='bike')),

    path('customer/', include(([

        path('dashboard', customer.CustomerDashboard, name='dashboard'),
        path('profile/<pk>', customer.CustomerProfile, name='customer_profile'),
        path('vendors/', customer.AllRestaurants, name='all-vendor'),
        path('vendorgood/<pk>/', customer.AllVendorGoods, name='all-vendors-good'),

        path('menu/', customer.AllMenu, name='all-menu'),

        path('foodgeneral/<name>/', general.FoodDetails, name='food-general'),


        path('mycart/<pk>/', customer.add_to_cart, name='add-to-cart'),
        path('myplugincart/<pk>/<food_pk>/', customer.add_to_cart_plugin, name='add-to-cart-plugin'),
        
        path('pluscart/<pk>/', customer.plus_to_cart, name='plus-to-cart'),
        
        path('summary/<get_total>/<total_plugin>/<total_package>/', customer.OrderSummaryView, name='order-summary'),
        
        
        path('minus/<pk>', customer.minus_to_cart, name='minus-to-cart'),
        path('minusplugin/<pk>/<food_pk>/', customer.minus_to_cart_plugin, name='minus-to-cart-plugin'),
        
        
        
        
        
        
        
        path('delete/<pk>', customer.remove_from_cart, name='delete-item'),
        path('deleteplugin/<pk>/<food_pk>/', customer.remove_from_cart_plugin, name='plugin-delete-item'),
        
        
        path('receipt', customer.OrderReceipt, name='order-receipt'),
        path('done/<pk>', customer.SuccessPayment, name='success-payment'),
        
        path('payment/<paid_amount>/<mins>/<distance>/<delivery_amount>/<food_amount>/<tax_amount>/<package_amount>/', customer.verifyPayment, name='verify-payment'),
        
     

        path('subscriptionpayment/<amount>/<mins>/<distance>', customer.verifyPaymentOrderSubscription, name='subscription-verify-payment'),


        path('packagepayment/<pk>/<amount>/<mins>/<distance>', customer.verifyPaymentPackage, name='package-verify-payment'),

        path('myorder', customer.MyOrder, name='my-order'),

        path('paymentfailed', customer.closePayment, name='failed-payment'),

        path('packagepaymentfailed/<pk>', customer.closePackagePayment, name='failed-package-payment'),


        path('parcelsending', customer.ParcelMessage, name='parcel-message'),
        
        path("parcelpackage/<pk>", customer.ParcelPackageDetails, name="parcel-package"),
        

        path("paymentparcelpackage/<int:pk>/<int:id>/", customer.PackagePayment, name="payment-parcel-package"),
        

        path("paymentparcelpackage/<pk>/<distance>/<code>/", customer.verifyPaymentPackageSubscription, name="payment-parcel-package-subscription"),
        


        path("editparcel/<pk>/<id>/", customer.EditParcelMessage, name="edit-parcel-message"),

        path("editparcelpackage/<int:pk>/<int:id>/", customer.EditParcelPackageDetails, name="edit-parcel-package-message"),
        
        


        #path("search/", customer.SearchRestaurants.as_view(), name="search-results"),

       

        path('myaddress', customer.MyAddress, name='my-address'),


        path('addressdelete/<int:id>/', customer.DeleteAddress, name='delete-address'),

        path('editdelete/<id>', customer.EditAddress, name='edit-address'),

        path('payondelivery/<pk>/<amount>/<mins>/<distance>/<receiver_code>', customer.PayOnDelivery, name='pay-on-delivery'),


         path('finalpackagereceipt/<int:pk>/', customer.FinalPackageReceipt, name='final-receipt'),

        path('finalorderreceipt/<int:pk>/', customer.FinalOrdergeReceipt, name='final-order-receipt'),
         

        path('finalpackagereceipt/<int:pk>/<int:id>/', customer.DeletPackage, name='delete-package'),


        path('updatemyprofile/<username>/', customer.CustomerProfileUpdate, name='update-my-profile'),

        path('passwordupdate/', customer.ChangePassword, name='change-password'),


        path('subscriptionackagedetails/<pk>/', customer.SubscriptionPackageDetails, name='subscription-package'),


        
         #path('verifypaymentpackage/<pk>/', customer.verifyPaymentPackage, name='verify-payment-package'),


        path('checksubscription/', customer.CheckSubscription, name='check-subscription'),
        
        
        path('password_change/', customer.CustomPasswordChangeView.as_view(), name='password_change'),
        
        path('profile/update/', customer.UserProfileUpdateView, name='user-update'),


        path('posprinting/<int:pk>/', customer.PosPrinting, name='pos-print'),

        
        path('updatepackages/', customer.UpdatePackages, name='update-packages'),
        
        path('addonpackage/<pk>/', customer.AddonWithPackage, name='add-on-package'),
        
   
        
        

       
    ], 'app'), namespace='customer')),
]


htmx_urlpatterns = [

    path('checkusername/', general.CheckUsername, name="check-username"),
    path('checkemail/', general.CheckEmail, name="check-email"),
    path('loadvendor/', general.load_vendor, name='load-vendor'),
    
]

urlpatterns += htmx_urlpatterns