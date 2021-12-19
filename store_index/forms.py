from django import forms
from django.core.exceptions import ValidationError 
from .models import *
from django.contrib.auth.models import User

class CustomerSignUpForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("FirstName", "LastName", "Email")
        widgets = {
            'Email': forms.EmailInput(attrs={'autofocus': ''})
        }

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)

class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("FirstName", "LastName", "Email", "PhoneNumber")
        help_texts = {
            'PhoneNumber': ('Area code is required. Must be United State phone number.'),
        }
        widgets = {
            'Email': forms.EmailInput(attrs={'autofocus': ''}),
            'PhoneNumber': forms.TextInput(attrs={'id': 'phoneNum', 'onblur': 'phoneNumberFormatter()'})
        }
    def clean_PhoneNumber(self):
        phone_number = self.cleaned_data['PhoneNumber']
        if len(phone_number) < 14:
            raise ValidationError("Phone number incorrectly formatted. Please enter 10-digit United States phone number.")
        return phone_number

class UsernameEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)
        help_texts = {
            'username': ('150 characters or fewer. Only letters, digits, and _ @ . + - allowed.'),
        }

# Newletter User sign up class.
class NewsletterSignUpForm(forms.ModelForm):
    class Meta:
        model = NewsletterUser
        fields = ['SubscriberEmail']
        labels = {
            'SubscriberEmail': 'Email',
        }

        # Normalize Email Function
        def NormalizeEmail(self):
            SubscriberEmail = self.NormalizedData.get('SubscriberEmail')

            # Returns
            return SubscriberEmail

# Newsletter creation class.
class NewsletterCreationForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['Subject', 'Body', 'Email', 'Status']
        widgets = {
            'Subject':forms.TextInput(attrs={'autofocus': ''}),
            
        }

# class CustomerForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = '__all__'

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("FirstName", "LastName", "Email", "PhoneNumber", "ShippingAddress", "ShippingCity", "ShippingZipCode", "ShippingState")
        widgets = {
            'FirstName': forms.TextInput(attrs={'autofocus': ''}),
            'Email': forms.EmailInput(),
            'PhoneNumber': forms.TextInput(attrs={'id': 'phoneNum', 'onblur': 'phoneNumberFormatter()'}),
            'ShippingZipCode': forms.TextInput(attrs={'maxlength':'5', 'id':'userZip'})
        }
    def __init__(self, *args, **kwargs):
        super(ShippingForm, self).__init__(*args, **kwargs)
        self.fields['FirstName'].required = True
        self.fields['LastName'].required = True
        self.fields['Email'].required = True
        self.fields['PhoneNumber'].required = True
        self.fields['ShippingAddress'].required = True
        self.fields['ShippingCity'].required = True
        self.fields['ShippingZipCode'].required = True
        self.fields['ShippingState'].required = True

# class BillingForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ("BillingAddress", "BillingCity", "BillingZipCode", "BillingState")
