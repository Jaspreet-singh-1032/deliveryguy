from django import forms
from django.db import transaction
from django.forms.utils import ValidationError
from app.models import *
from  django.contrib.auth.forms import  UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField, PasswordResetForm
from django.forms import (formset_factory, modelformset_factory)
# File: forms.py
from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput


class CustomerSignUpForm(UserCreationForm):

    #username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Enter Your Username', )),
                                #label=("Username"),  error_messages={'invalid': ("This value must contain only letters, numbers and underscores.")})
    username = forms.CharField(widget=forms.TextInput(attrs={'hx-target': '#username-error','hx-post': ('/checkusername/'),'hx-trigger': 'keyup delay:4s', 
                                                             'hx-swap':'outerhtml', 'max_length':30,
                                                             'placeholder': 'Enter Your Username', 'label':"Enter Username" }))                      
    first_name = forms.CharField(widget=forms.TextInput(
        attrs=dict(required=True, max_length=30, placeholder='First Name')), label = ("Surname"))
    last_name=forms.CharField(widget = forms.TextInput(
        attrs=dict(required=True, max_length=30, placeholder='Last Name')), label=("First Name"))
    password1=forms.CharField(widget=forms.PasswordInput(attrs = dict(
        required=True, max_length=30, render_value=False, placeholder='Enter Password')), label=("Password"))
    password2=forms.CharField(widget=forms.PasswordInput(attrs = dict(
        required=True, max_length=30, render_value=False, placeholder='Confirm Password')), label=("Confirm Password"))
    email=forms.EmailField(widget=forms.TextInput(attrs={'hx-target': '#email-error','hx-post': ('/checkemail/'),'hx-trigger': 'keyup', 'max_length':30,
                                                             'placeholder': 'Enter Your Email', 'required': True, })) 
    
    
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text=None

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(("The username already exists. Please try another one."))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # check and raise error if other user already exists with given email
        is_exists = User.objects.filter(email=email).exists()
        if is_exists:
            raise forms.ValidationError("User already exists with this email")
        return email
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(("The two password fields did not match."))
        return self.cleaned_data



    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', )

       
        username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'hx-target': '#username-error',
                'hx-post': ('check-username'),
                'hx-trigger': 'keyup[target.value.length > 3]'
                }
            )
        )

        

    def __init__(self, *args, **kwargs):
        ''' remove any labels here if desired
        '''
        super(CustomerSignUpForm, self).__init__(*args, **kwargs)

        # remove the label of a non-linked/calculated field (txt01 added at top of form)
        self.fields['first_name'].label = ''

        self.fields['last_name'].label = ''

        self.fields['email'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['username'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['password1'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['password2'].label = ''

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        ProfileCustomer.objects.create(user=user)
        return user


class BikeSignUpForm(UserCreationForm):
   
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30, placeholder='Enter Your Username')),
                                label=("Username"), error_messages={'invalid': ("This value must contain only letters, numbers and underscores.")})
    first_name = forms.CharField(widget=forms.TextInput(
        attrs=dict(required=True, max_length=30, placeholder='First Name')), label = ("Surname"))
    last_name=forms.CharField(widget = forms.TextInput(
        attrs=dict(required=True, max_length=30, placeholder='Last Name')), label=("First Name"))
    password1=forms.CharField(widget=forms.PasswordInput(attrs = dict(
        required=True, max_length=30, render_value=False, placeholder='Enter Password')), label=("Password"))
    password2=forms.CharField(widget=forms.PasswordInput(attrs = dict(
        required=True, max_length=30, render_value=False, placeholder='Confirm Password')), label=("Confirm Password"))
    email=forms.EmailField(widget=forms.TextInput(attrs = dict(
        required=True, max_lenght=50, placeholder='Enter Address')), label=("Email Address"))
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text=None


    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(("The username already exists. Please try another one."))
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(("The two password fields did not match."))
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        ''' remove any labels here if desired
        '''
        super(BikeSignUpForm, self).__init__(*args, **kwargs)

        # remove the label of a non-linked/calculated field (txt01 added at top of form)
        self.fields['first_name'].label = ''

        self.fields['last_name'].label = ''

        self.fields['email'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['username'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['password1'].label = ''

        # you can also remove labels of built-in model properties
        self.fields['password2'].label = ''

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', )

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_bike = True
        user.save()
        ProfileBike.objects.create(user=user)
        return user


class CustomerProfileForm(forms.ModelForm):
    CHOICES = [('1','Male'),('2','Female')]
    
    
    gender = forms.ChoiceField(
    
        widget=forms.Select(attrs={'class': 'star'}), choices=CHOICES
    )


    
    class Meta:
        model = ProfileCustomer
        exclude = ('updated_at', 'created_at', 'user')
        widgets = {
          'address': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }




    


class CheckoutForm(forms.ModelForm):
    shipping_address=forms.CharField(widget = forms.TextInput(
        attrs=dict(required=True, max_length=250, onFocus="geolocate()", placeholder='Enter Your Address')), label=("Delivery Address"))
   
    location = forms.ModelChoiceField(queryset=Location.objects.filter(), label="Select Your Location", empty_label="...Select location", required=True, blank=False, widget=forms.Select(attrs={'class': 'form-control select2'}))
    #phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', placeholder='Enter Your Address', error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed."))
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', widget=forms.TextInput(attrs=dict(required=True, max_length=15, placeholder='Enter Your Phone Number +234800008888', )), label=("Contact Phonenumber"),  error_messages={'invalid': ("Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed.")})


    class Meta:
        model = Order
        fields = ('shipping_address', 'location', 'ordernote', 'longitude', 'latitude', 'schedule', 'phone_number')


        widgets = {
          'ordernote': forms.Textarea(attrs={'rows':2, 'cols':100}),
          'longitude': forms.TextInput(attrs={'type': 'hidden'}),
          'latitude': forms.TextInput(attrs={'type': 'hidden'}),
          'schedule': DateTimePickerInput(),
       
        }
    
    


       
class DetailsForm(forms.ModelForm):

    myaddress=forms.CharField(widget = forms.TextInput(
        attrs=dict(required=True, max_length=250, onFocus="geolocate()", placeholder='Enter Your Address')), label=("Delivery Address"))
    location = forms.ModelChoiceField(queryset=Location.objects.filter(), label="Select Your Location", empty_label="...Select location", required=True, blank=False, widget=forms.Select(attrs={'class': 'form-control select2'}))
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', widget=forms.TextInput(attrs=dict(required=True, max_length=15, placeholder='Enter Your Phone Number +234800008888', )), label=("Contact Phonenumber"),  error_messages={'invalid': ("Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed.")})



    class Meta:
        model = DeliveryDetails
        fields = ('myaddress', 'message', 'nickname', 'location', 'phone_number')

       






class ReceiverDetailsForm(forms.ModelForm):
    class Meta:
        model = ReceiverDetails
        #fields = ('comment', 'rate')
        exclude = ['sender', 'created_at', 'updated_at', 'receiver_code', 'process']








class PackageDetailsForm(forms.ModelForm):
    class Meta:
        model = PackageDetails
        #fields = ('comment', 'rate')
        exclude = ['pay_on_delivery', 'subscription', 'tracking_number', 'user', 'bike', 'receiver_details', 'taken' , 'ongoing', 'created_at', 'updated_at', 'paid_amount', 'paid', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'mins', 'distance']



class BikeProfileForm(forms.ModelForm):

    
    class Meta:
        model = ProfileBike
        exclude = ('updated_at', 'created_at', 'user')











class UserChangeForm(UserChangeForm):
    
    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
           
           "<a href=\"..\..\passwordupdate\">this form</a>."

    
        ),
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)
        
        
        
        
class DeliveryPackageFormUpdate(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=DeliveryPackages.objects.filter(), empty_label=None, label="Select Your Delivery Package", required=True, blank=False, widget=forms.Select(attrs={'class': 'form-control select2'}))

    class Meta:
        model = DeliveryPackages
        fields = ['name', ]  # Only 'name' is displayed as radio buttons
        widgets = {
            'name': forms.CheckboxSelectMultiple
        }



 

        



class AddonForm(forms.ModelForm):
    
    name = forms.ModelMultipleChoiceField(queryset=AddonGoods.objects.all(),label="Select The Add Food You Want", widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = AddonGoods
        fields = ('name',) # Only 'name' is displayed as radio buttons
        
        
        
        
        
       

'''

class UserForm(UserChangeForm):
    
    #groups = forms.ModelMultipleChoiceField(label="Select User Groups", widget=forms.CheckboxSelectMultiple)
    password = forms.CharField(widget=forms.HiddenInput(), initial="value")
    
    class Meta:
        model = User
        #fields = "__all__"
        exclude = ('groups','user_permissions', 'is_superuser', 'date_joined', 'last_login', 'is_staff')
        
        

'class': "form-control"

class="col-lg-3 col-md-3 col-sm-12 form-group

class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = ProcessOrder
        exclude = ['created_at', 'updated_at',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].queryset = SubCategory.objects.none()

        if 'category' in self.data:
                try:
                    category_id = int(self.data.get('category'))
                    self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
                except (ValueError, TypeError):
                    pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategory_set.order_by('name')

SubCategoryFormset = modelformset_factory(
    SubCategory,
    fields=('name', ),
    extra=1,
    
    widgets = {
        'name': forms.Select(attrs={'id': 'subcategory'}),
    }
    
)




class ProcessFoodForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)



class SubCategoryForm(forms.ModelForm):

    INTEGER_CHOICES = [tuple([x,x]) for x in range(1,10)]

    quantity = forms.IntegerField(widget=forms.Select(choices=INTEGER_CHOICES))

    class Meta:
        model = SubCategory
        labels = {"Quantity": "Qty."}
        fields = ('name', 'quantity')

SubCategoryFormset = formset_factory(SubCategoryForm, extra=1)



class OrderCreateForm(forms.ModelForm):
    class Meta: 
        model = Order
        fields = []


class OrderEditForm(forms.ModelForm):
    INTEGER_CHOICES = [tuple([x,x]) for x in range(1,10)]

    quantity = forms.IntegerField(widget=forms.Select(choices=INTEGER_CHOICES))

    class Meta: 
        model = ProcessOrder
        fields = ('subcategory', 'quantity')








class BikeOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('shipping_address', 'ordernote', 'package',)


'''

