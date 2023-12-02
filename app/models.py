from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from autoslug import AutoSlugField
from ckeditor_uploader.fields import RichTextUploadingField 
from django.shortcuts import reverse
from django.template.defaultfilters import slugify 
from decimal import Decimal
from ckeditor_uploader.fields import RichTextUploadingField 
from django.utils.crypto import get_random_string
import random
import string
from django.utils.timezone import now



from django.dispatch import receiver
from django.db.models.signals import post_save
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

def random_string():
    value = 'DISHAXIS-'
    return value + str(random.randint(10000, 99999))


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 22.0
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))



class User(AbstractUser):
    is_bike = models.BooleanField('bikeman Users', default=False)
    is_customer = models.BooleanField('Customer Users', default=False)
    #is_investor = models.BooleanField('Invest Users', default=False)







class ProfileCustomer(models.Model):
    
    GENDER = (
        ('1', "Male"),
        ('2', "Female"),
    )
    

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField('Phone Number', max_length=25)
    gender = models.CharField('Gender', max_length=10, choices=GENDER)
    image = models.ImageField("Image of Customer", help_text='Passport Photograhpy of The Customer', upload_to='customer/', blank=True,  null=True)
    address = models.TextField("Address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.username


class ProfileBike(models.Model): 
    
    GENDER = (
        ('Male', "Male"),
        ('Female', "Female"),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField('Phone Number', max_length=25)
    image = models.ImageField("Image of Bike Man", help_text='Passport Photograhpy of The BikeMan', upload_to='bike/',  null=True)
    identification = models.ImageField("Means of identification", help_text="International Passport, BVN, Voters Card, Driver's driver license", upload_to='bike/',  null=True)
    gender = models.CharField('Gender', max_length=10, choices=GENDER)
    address = models.CharField("Permanent Address", max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.username
    


class Category(models.Model):
    name = models.CharField("Category of Food", max_length=50)
    icon = models.ImageField('Category Image', upload_to='category/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name}'

    def subcategory(self):
        if not hasattr(self, '_subcategory'):
            self._subcategory = self.subcategory.all()
        return self._subcategory
    '''
    def clean(self):
        if self.goal < 1:
            raise ValidationError('Only numbers equal to 1 or greater are accepted.')
    '''
    

    class Meta:
       
        verbose_name = 'Category of Foods'
        verbose_name_plural = 'Categories of Foods'






class Location(models.Model):

    name = models.CharField('Location', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return self.name










class Good(models.Model):
    
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', max_length=500)
    description = RichTextUploadingField(blank=True,null=True)
    addon = models.BooleanField("Does The Food Need Other Items", default=False)
    delivery = models.BooleanField("Does The Food Need Delivery Package", default=False)
    category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    stock = models.PositiveIntegerField("Numbers in Stock", default=0)
    number = models.PositiveIntegerField("Max Number Per Order", default=0)
    image = models.ImageField('Product Image', upload_to='products/%Y/%m/%d')
    available = models.BooleanField(default=True)
    deactivate = models.BooleanField(default=False)
    returnpolicy = RichTextUploadingField('Product Return Policy', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.name}' 
    
  
    class Meta:
        verbose_name = "Food Details"
        verbose_name_plural = "Food Details"

  

   
    def get_absolute_url(self):
        return reverse("web:vendor-detail", kwargs={"slug": self.slug})



    def get_add_to_cart_url(self):
        return reverse("web:add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("web:remove-from-cart", kwargs={'slug': self.slug})
    

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)





class GoodImageGallery(models.Model):
    food = models.ForeignKey(Good, on_delete=models.CASCADE)
    image = models.ImageField('Images of The Goods', upload_to='goods', blank=True, null=True)

    def __str__(self):
        return str(self.food.name)

    class Meta:
      
        verbose_name = 'Food Gallery'
        verbose_name_plural = 'Food Gallery'
        
        
        
class AddonGoods(models.Model):
    name = models.CharField('Add on Name', help_text='such as Ewedu Efo', max_length=250)
    image = models.ImageField('Images of The Add-on Goods', upload_to='addon', blank=True, null=True)
    #food = models.ManyToManyField(Good)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AddonGoods"
        verbose_name_plural = "Addon Foods"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("AddonGoods_detail", kwargs={"pk": self.pk})

class DeliveryPackages(models.Model):

    name = models.CharField("The Name for The Delivery Package", max_length=150)
    #price = models.DecimalField("The Price for The Package in Naira", max_digits=10, decimal_places=2, default=1.00)
    description = models.TextField("Description of the Package", null=True, blank=True)
    #price = models.PositiveIntegerField("The Price for The Package in Naira")
    price = models.DecimalField("The Price for The Package in Naira", max_digits=10, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "DeliveryPackages"
        verbose_name_plural = "DeliveryPackagess"

    def __str__(self):
        return self.name

    '''
    def get_absolute_url(self):
        return reverse("DeliveryPackages_detail", kwargs={"pk": self.pk})
    '''

class PluginFoods(models.Model):
    name = models.CharField("Name of The food", max_length=150)
    image = models.ImageField('Images of The Food', upload_to='plugin')
    price = models.DecimalField("The Price for The Package in Naira", max_digits=10, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plugin Foods"
        verbose_name_plural = "Plugin Foods"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("PluginFoods_detail", kwargs={"pk": self.pk})


class PluginOrderItem(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(PluginFoods, on_delete=models.CASCADE)
    foods =  models.ForeignKey(Good, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:
        verbose_name = "Plugin Order"
        verbose_name_plural = "Plugin Orders"

  
    
    def __str__(self):
        return f"Quantity(s): {self.quantity} Item Order For: {self.item.name} From: {self.foods}  ordered by {self.user.username}"






class OrderItem(models.Model):
       
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Good, on_delete=models.CASCADE)
    delivery = models.ForeignKey(DeliveryPackages, related_name='delivery', on_delete=models.CASCADE, null=True, blank=True) 
    ordered = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    addon = models.ManyToManyField(AddonGoods, blank=True)
    plugin = models.ManyToManyField(PluginOrderItem)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quantity(s): {self.quantity} Item Order For: {self.item.name} From: {self.item}  ordered by {self.user.username}"

    def get_total_plugin(self):
        total = 0
        for order_item in self.plugin.all():
            total += order_item.item.price * order_item.quantity
        return total 
        
    

    def get_total_item_price(self):
            return (self.quantity * self.item.price)
        
        
    
        
    def get_total_item_price_with_package(self):
        return (self.quantity * self.item.price)
    

    

    '''
    def get_sub_total_tax_total(self):
        tax = Decimal('0.075')
        tax_without_discount = self.get_total_item_price_with_package() + (self.get_total_item_price_with_package() * tax)
        return tax_without_discount
    '''


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=150, default=create_ref_code)
    bike = models.ForeignKey(User, related_name='bike', on_delete=models.CASCADE, blank=True, null=True)
    #deliveryPackages = models.ForeignKey(DeliveryPackages, related_name='delivery', on_delete=models.CASCADE, null=True, blank=True) 
    ordernote = models.TextField("Order Notes", null=True, blank=True,)
    schedule = models.DateTimeField("Schedule Delivery Time", default=now)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    shipping_address = models.CharField("Shipping Adresss", max_length=250, null=True)
    latitude = models.CharField("Latitude of Adresss",  null=True, max_length=250)
    longitude = models.CharField("Longitude of Adresss",  null=True, max_length=250)
    mins = models.CharField("Time To Deliver The Goods",  null=True, blank=True, max_length=250)
    distance = models.CharField("Distance To Deliver The Goods",  null=True, blank=True, max_length=250)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    food_amount = models.DecimalField("Amount Paid for Food", max_digits=10, decimal_places=2, default=1.00)
    paid_amount = models.DecimalField("Amount Paid for Total", max_digits=10, decimal_places=2, default=1.00)
    delivery_amount = models.DecimalField("Amount Paid For Delivery", max_digits=10, decimal_places=2, default=1.00)
    tax_amount = models.DecimalField("Amount Paid For Tax", max_digits=10, decimal_places=2, default=1.00)
    package_amount = models.DecimalField("Amount Paid For Package", max_digits=10, decimal_places=2, default=1.00)
    
    phone_number = models.CharField("Enter Your Phone Number", max_length=15, blank=True, null=True)
    #alpha=distance.distance.text|slice:':-2'|mul:settings.distance_price_food 
    ordered_date = models.DateTimeField()
    paid = models.BooleanField(default=False)
    subscription = models.BooleanField("Payment With Subscription", default=False)
    taken = models.BooleanField("being Taken by Bike Man", default=False)
    ongoing = models.BooleanField("Ongoing Order By Bike", default=False)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return f'{self.user.username} - {self.ref_code}'
    

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += Decimal(order_item.get_total_item_price())
        return total
    
    
    
    

    '''
    def get_total_package(self):
        total = 0
        for order_item in self.items.all():
            total+=Decimal(order_item.delivery.price)
        return total
            
    
    
    def get_tax_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_sub_total_tax_total()
        return total
    
    #validation
    def clean(self):
        super(BookForm, self).clean()

        title = self.cleaned_data.get('title')

        if len(title)<5:
            self.add_error('title','Can not save title less than 5 characters long')
            self.fields['title'].widget.attrs.update({'class': 'form-control  is-invalid'})

        return self.cleaned_data
     
    '''
    

    def save(self, *args, **kwargs):
        qr_image = qrcode.make(self.ref_code)
        qr_offset = Image.new('RGB', (310, 310), 'white')
        draw_img = ImageDraw.Draw(qr_offset)
        qr_offset.paste(qr_image)
        file_name = f'{self.ref_code}-{self.user.username}qr.png'
        stream = BytesIO()
        qr_offset.save(stream, 'PNG')
        self.qr_image.save(file_name, File(stream), save=False)
        qr_offset.close()
        super().save(*args, **kwargs)
     

    '''
    def generate_qr_code(self):
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"Your QR Code Data Here for {self.ref_code}")
        qr.make(fit=True)

        # Create an image from the QR code data
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a BytesIO object
        image_stream = BytesIO()
        img.save(image_stream, format="PNG")
        image_stream.seek(0)

        # Save the BytesIO object to the ImageField
        self.qr_code.save(f'qr_code_{self.ref_code}.png', File(image_stream), save=False)
        super().save()

    @receiver(post_save, sender=Order)
    def generate_qr_code(sender, instance, **kwargs):
        if not instance.qr_code:
            instance.generate_qr_code()
    '''



class DeliveryDetails(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField("Enter Your Phone Number", max_length=15, blank=True, null=True)
    myaddress = models.CharField("Delivery Address", max_length=250)
    latitude = models.CharField("Latitude of Adresss",  null=True, max_length=250)
    longitude = models.CharField("Longitude of Adresss",  null=True, max_length=250)
    location = models.ForeignKey(Location, related_name='mylocation', on_delete=models.CASCADE)
    message = models.CharField("Delivery Instructions", max_length=250)
    nickname = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"

    def __str__(self):
        return self.user.username
    

class Settings(models.Model):

    distance_price_food = models.FloatField("Price Per Kilometter for Food", null=True, blank=True)
    distance_price_package =  models.FloatField("Price Per Kilometter for Package", null=True, blank=True)
    '''
    payment_key = models.CharField('Enter Your Payment Key Here For Gateway', max_length=150, null=True, blank=True)
    payment_secret = models.CharField('Enter Your Payment SECRET Here For Gateway', max_length=150, null=True, blank=True)  
    google_map = models.CharField('Enter Your GOOGLE_API Key for Map', max_length=150, null=True, blank=True)   
    sms_api = models.CharField('Enter Your SMS API key', max_length=150, null=True, blank=True)   
    '''
    
    
    

    

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"




class ReceiverDetails(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField("Receiver Fullname", max_length=250)
    company_name = models.CharField("Company Name(if Applicable)", max_length=250, blank=True, null=True)
    picking_address = models.CharField("Pick Up Address", max_length=250)
    telephone = models.CharField("Pickup PhoneNumber", max_length=15)
    r_telephone = models.CharField("Reciever PhoneNumber", max_length=15)
    email = models.EmailField("Receiver Email address", max_length=254, null=True, blank=True)
    deliver_address = models.CharField("Reciever Delivery Address", max_length=250)
    receiver_code = models.CharField(max_length=150, default=create_ref_code)
    process = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Package Receiver"
        verbose_name_plural = "Package Receiver"

    def __str__(self):
        return f'{self.sender.username} - {self.receiver_code}'
    '''
    def get_absolute_url(self):
        return reverse("ReceiverDetails_detail", kwargs={"pk": self.pk})
    
    '''
    




class PackageDetails(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sender',  null=True, blank=True)
    bike = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    receiver_details = models.ForeignKey(ReceiverDetails, on_delete=models.CASCADE)
    nature_of_goods = models.CharField("Nature of The Parcel", help_text="Such As Letter, International Passport", max_length=250)
    image = models.ImageField("Image of Parcel", upload_to='parcel/',  null=True)
    values = models.CharField("Estimated Amount Value of the Parcel", help_text="The Value of the Goods in Naira", max_length=250)
    numbers = models.PositiveIntegerField("Numbers of The Parcel")
    weight = models.FloatField("Total Weight of the Parcel", help_text="The weight of the Parcel in KG", null=True, blank=True)
    dimensions = models.CharField("Dimension of the Package", help_text="23mm X 12mm", max_length=50, null=True, blank=True)
    
    instruction = models.TextField("Any Instruction of Delivery", null=True, blank=True)
    paid_amount = models.DecimalField("Paid Amount", max_digits=10, decimal_places=2, default=1.00)
    mins = models.CharField("Mintues to Delivery", max_length=10, null=True, blank=True)
    distance = models.CharField("Ditance to Delivery", max_length=10, null=True, blank=True)
    tracking_number = models.CharField("Tracking Number", max_length=100, null=True, blank=True)
    pay_on_delivery = models.BooleanField("Payment On Delivery Method", default=False)
    paid = models.BooleanField(default=False)
    subscription = models.BooleanField("Payment With Subscription", default=False)
    being_delivered = models.BooleanField(default=False)
    taken = models.BooleanField("being Taken by Bike Man", default=False)
    ongoing = models.BooleanField("Ongoing Order By Bike", default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Package Detail"
        verbose_name_plural = "Package Details"

    def __str__(self):
        return f'Reciever: {self.receiver_details.fullname} - {self.receiver_details.receiver_code}'

    def get_absolute_url(self):
        return reverse("PackageDetails_detail", kwargs={"pk": self.pk})




    
class SubscriptionPackage(models.Model):

    name = models.CharField("Subscription PAckage Name", max_length=250)
    distance = models.FloatField("Distance For the Package")
    price = models.FloatField("price For the PAckage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:
        verbose_name = "SubscriptionPackage"
        verbose_name_plural = "SubscriptionPackages"

    def __str__(self):
        return self.name





class Subscriber(models.Model):
    user = models.OneToOneField(User, related_name='subscriber', on_delete=models.CASCADE)
    package = models.ForeignKey('SubscriptionPackage', related_name='package', on_delete=models.CASCADE)
    paid = models.BooleanField("Payment Status")
    usage = models.FloatField("Distance Remains")
    active = models.BooleanField("Subscription Status")
    ref_code = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscriber"

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'



class LoginAdvert(models.Model):
    
    name = models.CharField("The Name of the Advert", max_length=50)
    image = models.ImageField("Image of Advertment", help_text='Upload IMage for the Advert', upload_to='advert/')
    website = models.URLField("", max_length=200, null=True, blank=True)
    active = models.BooleanField("Activate/Deactivate", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Login Advert"
        verbose_name_plural = "Login Adverts"

    def __str__(self):
        return self.name



class HomeAdvert(models.Model):
    
    name = models.CharField("The Name of the Advert", max_length=50)
    caption = models.CharField('Advert Caption Words', max_length=50,  null=True, blank=True)
    mcaption = models.CharField('Main Advert Caption Words, Single Word', max_length=50,  null=True, blank=True)
    othercaption = models.CharField('Other Advert Caption Words', max_length=150,  null=True, blank=True)
    image = models.ImageField("Image of Advertment", help_text='Upload Image for the Advert (1317PX X 520px)', upload_to='advert/')
    website = models.URLField("", max_length=200, null=True, blank=True)
    active = models.BooleanField("Activate/Deactivate", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home Page Advert"
        verbose_name_plural = "HomePage Adverts"

    def __str__(self):
        return self.name
    
    
    

class OpenHours(models.Model):
    days = models.CharField('Days of the Week', max_length=25)
    openTime = models.TimeField("Opening Time of the day")
    closingTime = models.TimeField("Closing Time of the day")    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    class Meta:
        verbose_name = "OpenHours"
        verbose_name_plural = "OpenHourss"

    def __str__(self):
        return f'{self.days} - {self.openTime} - {self.closingTime}'

    def get_absolute_url(self):
        return reverse("OpenHours_detail", kwargs={"pk": self.pk})





from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField



class BlogCategory(models.Model):

    name = models.CharField('Blog Category', help_text='Such As News, Update and Article', max_length=50)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categorys"

    def __str__(self):
        return self.name



class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    tags = TaggableManager()
    category  = models.ForeignKey(BlogCategory, related_name='blogcategory', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField("Activative/Deactivate", default=True)
    image = models.ImageField("Blog Image", help_text='Upload Image for the . Size is 620px X 461px', upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.slug)])

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

