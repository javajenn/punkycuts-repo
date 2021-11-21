from typing import Any, Dict
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
import requests, json
# from rest_framework.generics import CreateAPIView
# from store_index.models import Screenshot
# from store_index.serializers import ScreenshotCreateSerializer
# from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Customer
from .forms import *
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from .tokens import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from twilio.rest import Client 
from twilio.twiml.messaging_response import MessagingResponse

# Create your views here.
def index(request):
    distance = ''
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    request.session.set_test_cookie()
    if request.method == 'POST':
        zipcode = request.POST['zipCode']
        request.session['zipcode'] = zipcode

        headers = { 
            "apikey": "7b088940-393c-11ec-b8a2-09fe2745fd06"
        }

        params = (
            ("code", "45202"), 
            ("compare", zipcode),
            ("country", "us")
        );

        #response = requests.get("https://randomuser.me/api/")
        try:
            response = requests.get('https://app.zipcodebase.com/api/v1/distance', headers=headers, params=params);
        except requests.exceptions.ConnectionError:
            messages.add_message(messages.ERROR, 'Error connecting to zipcode service. Be aware we only ship to Cincinnati and some surrounding regions.')
        if response.status_code == 200:
            content = json.loads(response.text)
            results = content['results']
            if results:
                distance = results[zipcode]
            else:
                distance = .0123

    context = {
        'num_visits': num_visits,
        'distance': distance
    }

    return render(request, 'store_index/index.html', context)

def customize(request):
    if request.session.test_cookie_worked():
                print("The test cookie worked!!!")
                request.session.delete_test_cookie()
    return render(request, 'store_index/customize.html')

@login_required
def profile(request):
    user_form = UsernameEditForm()
    customer_form = CustomerEditForm()

    if request.user.is_staff:
        #customer = 'staff'
        # pk = str(request.user.pk)
        # link = '/admin/auth/user/' + pk
        return redirect('/admin')
    else:    
        userid = request.user.pk
        user_form = UsernameEditForm(instance=request.user)
        try:
            customer = Customer.objects.get(User_id=userid)
            customer_form = CustomerEditForm(instance=customer)
        except Customer.DoesNotExist:
            customer = None

    if not customer.is_email_verified:
        messages.add_message(request, messages.ERROR, 'Email is not verified. Please check inbox and spam folder.')
        return redirect('index')

    if request.method == 'POST':
        customer_form = CustomerEditForm(request.POST, instance=customer)
        user_form = UsernameEditForm(request.POST, instance=request.user)
        if customer_form.is_valid() and user_form.is_valid():
            customer_form.save()
            user = user_form.save()
            if 'Email' in customer_form.changed_data:
                email = customer_form.cleaned_data['Email']
                user.email = email
                user.save()



    context = {
        'customer': customer,
        'customer_form': customer_form,
        'user_form': user_form
    }
    return render(request, 'store_index/profile.html', context)

def handle_sms(request):
    if request.method == 'POST':
        body = request.values.get('Body', None)
        resp = MessagingResponse()
        resp.message('We have received your message. The admin will be in touch shortly.')

    return HttpResponse('hi')

class CustomerDetail(generic.DetailView):
    model = Customer
    template_name='store_index/profile.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_verify_email(user, request, customer):
    current_site = get_current_site(request)
    email_subject = 'Activate your account!'
    email_body = render_to_string('store_index/activate.html', {
        'user': user,
        'customer': customer,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_FROM_USER, to=[user.email])
    
    EmailThread(email).start()

def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        customer = Customer.objects.get(User_id=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        customer.is_email_verified = True
        customer.save()

        messages.add_message(request, messages.SUCCESS, 'Email verified. You may now access your user profile and message inbox.')
        return redirect('profile')

    return render(request, 'store_index/activation-failed.html', {'user': user})

def signup(request):
    user_form = UserCreationForm()
    customer_form = CustomerSignUpForm()
    email_form = UserEmailForm()

    if request.method == 'POST':
        customer_form = CustomerSignUpForm(request.POST)
        user_form = UserCreationForm(request.POST)
        #email_form = UserEmailForm(request.POST)
        #if email_form.is_valid():
            #print(customer_form.fields.Email) NOPE
            #print(customer_form.fields['Email'])
            #customer_form.cleaned_data['Email'] = email_form.cleaned_data['email']
        if customer_form.is_valid():
            if user_form.is_valid():
                new_user = user_form.save()
                print(new_user.email)
                new_user.email = customer_form.cleaned_data['Email']
                new_user.save()
                customer = customer_form.save()
                new_user = authenticate(username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password1'],)
                customer.User_id = new_user.pk
                customer.save()
                login(request, new_user)
                send_verify_email(new_user, request, customer)
                messages.add_message(request, messages.SUCCESS, 'Thank you for signing up! ')
                return redirect('index')#, {'customer': customer, 'user': new_user})

# What I'm thinking:
#   Create form for saving user email and just also save it to that!! See if there's already oform for this....
#
    context  = {
        'user_form': user_form,
        'customer_form': customer_form,
        'email_form': email_form
    }

    return render(request, 'store_index/signup.html', context)

class CustomerListView(generic.ListView):
    model = Customer

# class saveScreenshot(CreateAPIView):
#     serializer_class = ScreenshotCreateSerializer
#     permission_classes = [AllowAny]