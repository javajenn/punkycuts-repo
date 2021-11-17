from django import forms
from django.core.exceptions import ValidationError 
from .models import Customer
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
        fields = ("FirstName", "LastName", "Email", "PhoneNumber", "ShippingAddress", "ShippingCity", "ShippingZipCode", "ShippingState", "BillingAddress", "BillingCity", "BillingZipCode", "BillingState")
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