from datetime import date, datetime, timedelta
from typing import Any, Dict
from django.contrib import messages
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.context import RequestContext
import requests, json
# from rest_framework.generics import CreateAPIView
# from store_index.models import Screenshot
# from store_index.serializers import ScreenshotCreateSerializer
# from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.db.models import F
from store_index.context_processors import *
from .models import *
from .forms import *
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from .tokens import generate_token
from django.core.mail import EmailMessage, message, send_mail
from django.conf import settings
import threading
from twilio.rest import Client 
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
from postman.forms import WriteForm
from django.forms.models import model_to_dict
from django.core import serializers
import random
import string

# Create your views here.
def index(request):
    context = {}
    distance = ''
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    request.session.set_test_cookie()
    if request.method == 'POST':
        if 'zipCode' in request.POST:
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
                messages.add_message(request, messages.ERROR, 'Error connecting to zipcode service. Be aware we only ship to Cincinnati and some surrounding regions.')
            if response.status_code == 200:
                content = json.loads(response.text)
                results = content['results']
                if results:
                    distance = results[zipcode]
                else:
                    distance = None
    
    #cartsession = request.session.session_key
    #try:
    #    cart = Cart.object.filter(Session=cartsession)
    #    context.update({'cart': cart})
    #except:
    #    cart = None


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
        return redirect('punkydashboard')
    else:    
        userid = request.user.pk
        user_form = UsernameEditForm(instance=request.user)
        try:
            customer = Customer.objects.get(User_id=userid)
            customer_form = CustomerEditForm(instance=customer)
        except Customer.DoesNotExist:
            customer = None

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

@csrf_exempt
def handle_sms(request):

    def sms_to_msg(msg, sender):
        #TO DO - need to pass this to write view or something using user phone number and body and yeah
        try:
            customer = Customer.objects.get(PhoneNumber=sender)
        except:
            return
        
        form = WriteForm()
        form.subject = 'SMS from: ' + sender
        form.body = msg
        form.data = {'subject': form.subject, 'body': form.body}
        form.cleaned_data = {'subject': form.subject, 'body': form.body}
        form.save()

    msg = request.POST.get('Body', '')
    sender = request.POST.get('From', '')
    sender = sender.replace('+1', '(')
    sender = sender[0:4] + ') ' + sender[4:7] + '-' + sender[7:11]
    sms_to_msg(msg, sender)
    
    response = MessagingResponse()
    response.message('We have received your message. The admin will be in touch shortly.')

    return HttpResponse(str(response))

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
                return redirect('profile')#, {'customer': customer, 'user': new_user})

# What I'm thinking:
#   Create form for saving user email and just also save it to that!! See if there's already oform for this....
#
    context  = {
        'user_form': user_form,
        'customer_form': customer_form,
        'email_form': email_form
    }

    return render(request, 'store_index/signup.html', context)


def products(request, cat=''):
    heading = ''
    images = Image.objects.all()
    if cat != '':
        category = Category.objects.filter(slug=cat)
        try:
            cat1 = Category.objects.get(slug=cat)
            heading = 'Category: ' + cat1.Name
        except:
            pass
        try:
            products = Product.objects.filter(Product_Categories__in=category).order_by('Name')
        except:
            products = {}
        if heading == '':
            heading = "Can't find this category."      
    else:
        products = Product.objects.all().order_by('Name')
        heading = 'All Products'

    for product in products:
        product.images = Image.objects.filter(Product=product)

    return render(request, 'store_index/products.html', {
        "products": products,
        "images": images,
        "heading": heading
    })

def products_categories(request, cat):
    all_products = Product.objects.all()
    all_product_values = Product.objects.all().values()
    images = Image.objects.all()

    #output_products = []

    i = 0

    # for product in all_products:
    #     categories = all_products[i].Product_Categories.all().values()
    #     for category in categories:
    #         if category['slug'] == cat:
    #             output_products.append(all_product_values[i])
    #             output_products[len(output_products) - 1]['categories'] = []
    #             for prod_cat in categories:
    #                 output_products[len(output_products) - 1]['categories'].append(prod_cat['Name'])
    #     i += 1

    products

    return render(request, 'store_index/products.html', {
        "products": products,
        "slug": cat,
        "images": images,
    })

def product_details(request, slug):
    context = {}
    product = Product.objects.get(slug=slug)
    #productValues = list(Product.objects.filter(slug=slug).values())
    #productJson = JsonResponse(json.dumps(productValues))
    if product is not None:
        dProduct = model_to_dict(product)
        print(dProduct)
    try:
        images = Image.objects.filter(Product_id=product.id)
        context.update({'images': images})
    except Image.DoesNotExist:
        pass

    #globalVars = RequestContext(request, {}, {cartFunct})
    g = RequestContext(request, processors=[cartFunct])
    #gl = RequestContext(request).get()
    glbCart = g.get('globalCart')
    #print(glbCart)

    #sizes = Size.objects.all()
    sizes = product.Sizes.all()
    context.update({'sizes': sizes})
    #OrderProduct.objects.select_related('order').filter(orderDate__range=[WeeklyDate, TodaysDate])
    

    if request.method == 'POST':
        pageUrl = request.META.get('HTTP_ORIGIN') + request.META.get('PATH_INFO')
        if request.POST.get('backUrl') == pageUrl:
            pass
        else:
            originalbackUrl = request.POST.get('backUrl')
            request.session['backUrl'] = originalbackUrl

        #request.session['cart'] = product
        cartsession = request.session.session_key
        try:
            cart = Cart.objects.get(Session=cartsession)
        except Cart.DoesNotExist:
            cart = Cart(Session=cartsession)
            try:
                if request.user.customer:
                    cart.Customer = request.user.customer
            except: 
                pass
        cart.save()
        cartid = cart.id
        cartproducts = CartProduct.objects.filter(Q(Cart__Session=cartsession))

        if request.POST.get('size') != '':
            size = Size.objects.get(Product_Size=request.POST['size'])
            cartproduct = CartProduct(Cart_id=cartid, Product_id=product.id, Quantity=1, Size=size)
        else:
            cartproduct = CartProduct(Cart_id=cartid, Product_id=product.id, Quantity=1)
        equality = False
        maxQuantityPerProduct(request)
        maxQuantity = len(request.maxPerProduct)
        if not cartproducts:
            cartproduct.save()
            global_cart = cartFunct(request)
            cart = global_cart['globalCart']
            subtotal = cart.cart.Subtotal
            return JsonResponse({'quantity': cartproduct.Quantity, 'subtotal': subtotal, 'backUrl': request.session['backUrl']})
        else:
            for cp in cartproducts:
                if cp.Cart_id == cartproduct.Cart_id and cp.Product_id == cartproduct.Product_id and cp.Size == cartproduct.Size:
                    equality = True
                    crtprd = cp
            if equality == True:
                cartproduct = crtprd
                if cartproduct.Quantity < maxQuantity:
                    cartproduct.Quantity += 1
                    cartproduct.save()
                    global_cart = cartFunct(request)
                    print(global_cart)
                    cart = global_cart['globalCart']
                    subtotal = cart.cart.Subtotal
                    # for c in global_cart:
                    #     cart = c['cart']
                    #     subtotal = cart.Subtotal
                    #RequestContext(request)
                    return JsonResponse({'quantity': cartproduct.Quantity, 'subtotal': subtotal, 'backUrl': request.session['backUrl']})
                else:
                    #messages.add_message(request, messages.ERROR, 'We only allow a maximum quantity of 12 at this time.')
                    #msg = request._messages._queued_messages[0]
                    #newmsg = {
                        #   'extra_tags': msg.extra_tags,
                        #  'level': msg.level,
                        #  'message': msg.message,
                        #  'tags': msg.tags
                    #}
                    #print(messages)
                    #updateMessages(request)
                    global_cart = cartFunct(request)
                    cart = global_cart['globalCart']
                    subtotal = cart.cart.Subtotal
                    return JsonResponse({'quantity': cartproduct.Quantity, 'subtotal': subtotal, 'messages': 'newMessage', 'backUrl': request.session['backUrl']})
            else:
                cartproduct.save()
                return JsonResponse({'quantity': cartproduct.Quantity, 'backUrl': request.session['backUrl']})
        # make a new instance of cart model! but not every time.. 
        #pass

    #dProduct = json.dumps(product)
    #dProduct = serializers.serialize("json", Product.objects.get(slug=slug))

    context.update({
        "product": product,
        "dProduct": dProduct,
    })

    return render(request, 'store_index/product_details.html', context)

def smallbusiness(request):

    return render(request, 'store_index/smallbusiness.html')
# class saveScreenshot(CreateAPIView):
#     serializer_class = ScreenshotCreateSerializer
#     permission_classes = [AllowAny]

def checkout_shipping(request):

    form = ShippingForm()

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            form.save()
            customer_email = form.cleaned_data['Email']
            customer = Customer.objects.filter(Email=customer_email).values()
            return redirect(checkout_billing, customer_id=customer[0]['CustomerID'])

    context = {'form': form}
    return render(request, 'store_index/checkout_shipping.html', context)

def checkout_billing(request, customer_id):
    customer_for_order = Customer.objects.get(id=customer_id)

    prods_in_cart = Product.objects.all()
    prods_values = Product.objects.all().values()
    total_price = 0
    product_ids = []

    for index in range(len(prods_in_cart)):
        product_price = prods_values[index]['Price']
        total_price += product_price

    for product in prods_values:
        product_ids.append(product['id'])
    
    images = Image.objects.all()
    return render(request, 'store_index/checkout_billing.html', {
        'customer': customer_for_order,
        'total_price': total_price,
        'products': prods_in_cart,
        'product_id_list': product_ids,
        'images': images
    })

def checkout_complete(request):
    if request.method == 'POST':
        # Get data sent and create the order in the database
        body = json.loads(request.body)
        print('BODY:', body)

        customer = Customer.objects.get(id=body['customer_ID'])

        order = Order.objects.create(Customer_id=customer)
        order.save()

        return JsonResponse('Order Completed!', safe=False)

def handle_cart(request):
    cartsession = request.session.session_key
    globalCart = CartProduct.objects.filter(Q(Cart__Session=cartsession))
    subtotal = 0
    if request.method == 'POST':
        if 'quantity' in request.POST:
            overq = 'false'
            quantity = request.POST['quantity']
            product = Product.objects.get(id=request.POST['productid'])
            cartproduct = CartProduct.objects.get(id=request.POST['cp'])
            if cartproduct.Product.Status.Description == 'In Stock':
                inv = Inventory.objects.get(Product= cartproduct.Product, Size=cartproduct.Size)
                if int(quantity) > inv.Quantity:
                    cartproduct.Quantity = inv.Quantity
                    messages.add_message(request, messages.ERROR, 'There are less items in stock than you\'re trying to add. Cart has been updated to reflect current inventory.')
                    overq = 'true'
                else:
                    cartproduct.Quantity = quantity
            cartproduct.save()
            global_cart = cartFunct(request)
            cart = global_cart['globalCart']
            subtotal = cart.cart.Subtotal
            return JsonResponse({'subtotal': subtotal, 'overQuantity':overq})
        elif 'removeProd' in request.POST:
            p_id = request.POST['removeProd']
            #selectedCp = CartProduct.objects.get(id=request.POST['cp'])
            product = Product.objects.get(id=p_id)
            # maybe i can send the size and filter instead of get 
            cartproduct = CartProduct.objects.get(id=request.POST['cp'])
            cartproduct.delete()
            global_cart = cartFunct(request)
            cart = global_cart['globalCart']
            if cart is not None:
                subtotal = cart.cart.Subtotal
            quantity = globalCart.count() 
            return JsonResponse({'subtotal': subtotal, 'quantity': quantity})

        
    return HttpResponse("updated")
@login_required
def punkydashboard(request):
    if request.user.is_staff:
        return render(request, 'store_index/punkydashboard.html')
    else:
        return redirect('profile')

# Newsletter Sign Up View
def NewsletterSignUp(request):
    Form = NewsletterSignUpForm(request.POST or None)

    # Checking Valid Data
    if Form.is_valid():

        Instance = Form.save(commit=False)

        # Fail and inform user if email is already in the database.
        if NewsletterUser.objects.filter(SubscriberEmail=Instance.SubscriberEmail).exists():
            messages.warning(request, 'This email already exists.', 'alert alert-warning alert-dismissable')

        # Save and inform user when email is successfully subscribed to mailing list.
        else:
            Instance.save()
            messages.success(request, 'Success. Thank you for subscribing!', 'alert alert-success alert-dismissible')

        # Email Script
        subject = "Thank you for subscribing to Punky Cuts Newsletter!"
        from_email = settings.EMAIL_HOST_USER
        to_email = [Instance.SubscriberEmail]
        signup_message = """Welcome! Thank you for subscribing to PunkyCuts newsletter. You will recieve updates and news for our store. Be sure to check us out on instagram as well at https://www.instagram.com/punkycuts/. To unsubscribe to this newletter click here https://punkycuts.pythonanywhere.com/newsletter/unsubscribe/."""
        send_mail(subject=subject, from_email=from_email, recipient_list=to_email, message=signup_message, fail_silently=True)

    Context = {
        'Form': Form,
    }

    Template = "store_index/newsletterSignup.html"

    # Returns
    return render(request, Template, Context)

# Newsletter Unsubscribe View
def NewsletterUnsubscribe(request):
    Form = NewsletterSignUpForm(request.POST or None)

    # Check Valid Data
    if Form.is_valid():
        Instance = Form.save(commit=False)

        # Save and inform user when successfully deleted.
        if NewsletterUser.objects.filter(SubscriberEmail=Instance.SubscriberEmail).exists():
            NewsletterUser.objects.filter(SubscriberEmail=Instance.SubscriberEmail).delete()
            messages.success(request, 'Successfully unsubscribed. Sorry to see you go!', 'alert alert-success alert-dismissible')

            # Email Script
            subject = "Punky Cuts Unsubscribe"
            from_email = settings.EMAIL_HOST_USER
            to_email = [Instance.SubscriberEmail]
            unsubscribe_message = """Sorry to see you go, thank you for your patronage."""
            send_mail(subject=subject, from_email=from_email, recipient_list=to_email, message=unsubscribe_message, fail_silently=True)

        # Fail and inform user if unsubcribing a nonsubscribed email.
        else:
            messages.warning(request, 'Sorry, that email is not subscribed to our mailing list.', 'alert alert-warning alert-dismissible')

    Context = {
        'Form': Form,
    }

    Template = "store_index/unsubscribe.html"

    # Returns
    return render(request, Template, Context)

# Control Newsletter
def ControlNewsletter(request):
    if request.user.is_staff:

        # Check if user us staff.
        Form = NewsletterCreationForm(request.POST or None)

        # Check valid form
        if Form.is_valid():
            Instance = Form.save()
            newsletter = Newsletter.objects.get(id=Instance.id)
            if newsletter.Status == "Published":
                Subject = newsletter.Subject
                Body = newsletter.Body
                from_email = settings.EMAIL_HOST_USER
                for Email in newsletter.Email.all():
                    send_mail(subject=Subject, from_email=from_email, recipient_list=[Email], message=Body, fail_silently=True)
                messages.success(request, 'Newsletter submitted.', 'alert alert-success alert-dismissible')

        Context = {
            'Form': Form,
        }

        Template = "store_index/writeNewsletter.html"

        # Returns
        return render(request, Template, Context)
    
def checkout(request):
    context = {}#{'guest': 'false'}
    try:
        cust = request.user.customer
        shipForm = ShippingForm(instance=cust)
    except:
        shipForm = ShippingForm()
    context.update({'shipForm':shipForm})

    if 'guest' in request.session:
        if request.session['guest'] == 'true':
            context.update({'guest': 'true'})

    global_cart = cartFunct(request)
    global_cart = global_cart['globalCart']
    for cp in global_cart:
        if cp.Product.Status.Description == 'In Stock':
            inv = Inventory.objects.get(Product=cp.Product, Size=cp.Size)
            q = inv.Quantity
            if cp.Quantity > q:
                cp.Quantity = q
                cp.save()
                messages.add_message(request, messages.ERROR, 'Quantity of items in your cart have been adjusted based on current inventory.')

                
    if request.method == 'POST':
        postGuest = request.POST.get('guest') 
        sessionGuest = request.session.get('guest')
        if postGuest == 'true':
            context.update({'guest': 'true'})
            request.session['guest'] = 'true'

        if 'zip' in request.POST:
            zipcode = request.POST['zip']

            headers = { 
                    "apikey": "7b088940-393c-11ec-b8a2-09fe2745fd06"
                }

            params = (
                ("code", "45202"), 
                ("compare", zipcode),
                ("country", "us")
            );

            try:
                response = requests.get('https://app.zipcodebase.com/api/v1/distance', headers=headers, params=params);
            except requests.exceptions.ConnectionError:
                messages.add_message(request, messages.ERROR, 'Error connecting to zipcode service. Be aware we only ship to Cincinnati and some surrounding regions.')
            if response.status_code == 200:
                content = json.loads(response.text)
                results = content['results']
                if results:
                    distance = results[zipcode]
                    if distance > 200:
                        return JsonResponse({'status': 'out-of-range'})
                else:
                    distance = None
                    return JsonResponse({'status': 'distance-none'})
        try:
            customer = request.user.customer
        except:
            customer = None
            if 'firstName' in request.POST:
                fName = request.POST['firstName']
                lName = request.POST['lastName']
                email = request.POST['email']
                phone = request.POST['phone']
                zipcode = request.POST['zip']

        checkout = request.POST.get('approved')
        status = request.POST.get('status')
        if checkout == 'true' and status == 'COMPLETED':
            # do checkout tings here.
            data = json.loads(request.POST.get('data'))
            adr1 = data['address_line_1']
            if 'address_line_2' in data:
                adr2 = data['address_line_2']
            state = data['admin_area_1']
            city = data['admin_area_2']
            country = data['country_code']
            zipcode = data['postal_code']
            total = request.POST.get('total')
            # MAKE SURE TO REMOVE SESSION VAR FOR GUEST OR SET TO FALSE!! JENN TO DO!!
            global_cart = cartFunct(request)
            global_cart = global_cart['globalCart']
            print(global_cart)
            if customer is None:
                customer = Customer(FirstName=fName, LastName=lName, Email=email, PhoneNumber=phone, ShippingAddress=str(adr1+ " " +adr2), ShippingCity=city, ShippingZipCode=zipcode, ShippingState=state)
                customer.save()
            newOrder = Order(Customer=customer, Date=datetime.now(), Total=total)
            newOrder.save()
            counter = 0
            for cp in global_cart:
                print(cp)
                newOrderProduct = OrderProduct()
                newOrderProduct.Order = newOrder
                newOrderProduct.Product = cp.Product
                newOrderProduct.Quantity = cp.Quantity
                newOrderProduct.Size = cp.Size
                if newOrderProduct.Product.Status.Description == 'In Stock':
                    inv = Inventory.objects.get(Product=newOrderProduct.Product, Size=newOrderProduct.Size)
                    inv.Quantity -= newOrderProduct.Quantity
                    inv.save()
                    if inv.Quantity == 0:
                        product = Product.objects.get(id=newOrderProduct.Product.id)
                        stat = Status.objects.get(Description='Out of Stock')
                        product.Status = stat
                        product.save()
                newOrderProduct.save()
            return JsonResponse({'orderId': newOrder.id})
            #return render(request, 'store_index/confirmation.html', context)


    if 'zipcode' in request.session:
        context.update({'zip':request.session['zipcode']})
    else:
        context.update({'zip':None})
    
    cartFunct(request)
    context.update({'cartdisabled':'true'})
    return render(request, 'store_index/checkout.html', context)

def financial(request):    
    # Statistic Reports
    assert isinstance(request, HttpRequest)
    countContext = {}
    context = {}
   
    ##inventory in STOCK
    # TShirtCount = Product.objects.filter(Name='T-Shirt')
    # LongSleeveShirtCount = Product.objects.filter(Name='Long Sleeve Shirt')
    # BabyOnesieCount = Product.objects.filter(Name='Baby Onesie')
    # MugCount = Product.objects.filter(Name='Mug')
    # BagCount = Product.objects.filter(Name='Bag')
    # WaterBottleCount=Product.objects.filter(Name='Water Bottle')   
    # ProductCount = Product.objects.all().aggregate(Sum('Quantity'))
    # ProductQ=ProductCount['Quantity__sum']
       
    ##sold items count
    pTypes = Type.objects.all()
    context.update({'types':pTypes})
    for type in pTypes:
        t = type.Product_Type
        filt = OrderProduct.objects.filter(Q(Product__Type=type)).aggregate(Sum('Quantity'))
        filtCount = filt['Quantity__sum']
        if filtCount is None:
            filtCount = 0
        #var = 'sold' + type.Product_Type + 'Count'
        countContext.update({t: filtCount})
    print(countContext)
    
    type = Type.objects.get(Product_Type='T-Shirt')
    soldTShirtCount = OrderProduct.objects.filter(Q(Product__Type=type)).aggregate(Sum('Quantity'))
    soldTShirtQ=soldTShirtCount['Quantity__sum']
    if soldTShirtQ is None:
        soldTShirtQ = 0

    soldLongSleeveCount=OrderProduct.objects.filter(Product_id=3).aggregate(Sum('Quantity'))
    soldLongSleeveQ=soldLongSleeveCount['Quantity__sum']
    if soldLongSleeveQ is None:
        soldLongSleeveQ = 0

    soldBabyOnesieCount = OrderProduct.objects.filter(Product_id=18).aggregate(Sum('Quantity'))
    soldBabyOnesieQ=soldBabyOnesieCount['Quantity__sum']
    if soldBabyOnesieQ is None:
        soldBabyOnesieQ = 0

    soldMugCount = OrderProduct.objects.filter(Product_id=5).aggregate(Sum('Quantity'))
    soldMugQ=soldMugCount['Quantity__sum']
    if soldMugQ is None:
        soldMugQ = 0
    
    soldBagCount = OrderProduct.objects.filter(Product_id=16).aggregate(Sum('Quantity'))
    soldBagQ=soldBagCount['Quantity__sum']
    if soldBagQ is None:
        soldBagQ = 0

    soldWaterBottleCount = OrderProduct.objects.filter(Product_id=17).aggregate(Sum('Quantity'))
    soldWaterBottleQ=soldWaterBottleCount['Quantity__sum']
    if soldWaterBottleQ is None:
        soldWaterBottleQ = 0    
   
    # Financial Reports
    TodaysDate = datetime.today()
    #WeeklyDate = TodaysDate+relativedelta(weeks=-1)
    WeeklyDate = date.today()-timedelta(days=7)    
    MonthlyDate = date.today()-timedelta(days=30)
    AnnualDate = date.today()-timedelta(days=365)
    #AnnualDate = TodaysDate+relativedelta(years=-1)    
     
    ##total for the purchase: its the sum of price*quantity
    total_purchases=OrderProduct.objects.all().aggregate(total_cos=Sum(F('Price') * F('Quantity')))
    GrossSales=total_purchases['total_cos']     
    
    ##
    ##total_weekly=OrderProduct.objects.filter(order__in=Order.objects.filter(orderDate__range=[WeeklyDate, TodaysDate])).aggregate((Sum('total_price'))) 
    ##cc=total_weekly['total_price__sum']  
    
    ##weekly sales  
    weekly=Order.objects.filter(Date__range=[WeeklyDate, TodaysDate]) 
    total_weekly=OrderProduct.objects.filter(Order__in=Order.objects.filter(Date__range=[WeeklyDate, TodaysDate])).aggregate(total_cos=Sum(F('Price') * F('Quantity'))) 
    GrossWeeklySales=total_weekly['total_cos']
    
    ##monthly sales
    monthly=Order.objects.filter(Date__range=[MonthlyDate, TodaysDate])
    total_monthly=OrderProduct.objects.filter(Order__in=Order.objects.filter(Date__range=[MonthlyDate, TodaysDate])).aggregate(total_cos=Sum(F('Price') * F('Quantity')))
    GrossMonthlySales=total_monthly['total_cos']
    
    ##annual sales
    annual=Order.objects.filter(Date__range=[AnnualDate, TodaysDate])
    total_annual=OrderProduct.objects.filter(Order__in=Order.objects.filter(Date__range=[AnnualDate, TodaysDate])).aggregate(total_cos=Sum(F('Price') * F('Quantity')))
    GrossAnnualSales=total_annual['total_cos']   
    
    for c in countContext:
        pass

    # Tax Calculations
    def CalculateTaxes(GrossPay):
        TaxedPay = float(GrossPay) * .95
        return TaxedPay

    #Tax is based off paypal percentage + website deployment cost. Business does not gross enough to pay taxes.            
    if GrossWeeklySales is not None:
        TaxedWeeklySales = CalculateTaxes(GrossWeeklySales)  
    else:
        TaxedWeeklySales = 0
        GrossWeeklySales = 0

    if GrossMonthlySales is not None:
        TaxedMonthlySales = CalculateTaxes(GrossMonthlySales) 
    else:
        TaxedMonthlySales = 0
        GrossMonthlySales = 0

    if GrossAnnualSales is not None:   
        TaxedAnnualSales = CalculateTaxes(GrossAnnualSales)
    else:
        TaxedAnnualSales = 0
        GrossAnnualSales = 0

    if GrossSales is not None:
        TaxedGrossSales = CalculateTaxes(GrossSales)
    else: 
        TaxedGrossSales = 0
        GrossSales = 0

    context = {
        # 'ProductCount': ProductCount,
        # 'TShirtCount': TShirtCount,
        # 'LongSleeveShirtCount' : LongSleeveShirtCount,
        # 'BabyOnesieCount': BabyOnesieCount,
        # 'MugCount': MugCount,  
        # 'BagCount' : BagCount,
        # 'WaterBottleCount': WaterBottleCount,
        #'ProductQ': ProductQ,
        'WeeklyDate' : WeeklyDate,    
        'weekly':weekly,
        'MonthlyDate': MonthlyDate,        
        'total_purchases' : total_purchases,         
        'weekly':weekly,
        'monthly':monthly,
        'total_monthly' :total_monthly,
        'total_weekly': total_weekly,
        'total_annual' :total_annual,
        'annual':annual,
        'GrossSales':GrossSales,
        'TaxedGrossSales':TaxedGrossSales,      
        'GrossWeeklySales': GrossWeeklySales,
        'TaxedWeeklySales': TaxedWeeklySales,
        'GrossMonthlySales': GrossMonthlySales,
        'TaxedMonthlySales': TaxedMonthlySales,
        'GrossAnnualSales': GrossAnnualSales,
        'TaxedAnnualSales': TaxedAnnualSales,                         
        'TaxedAnnualSales':TaxedAnnualSales,
        'soldTShirtCount' :soldTShirtCount,
        'soldTShirtQ':soldTShirtQ,
        'soldTShirtQ': soldTShirtQ,
        'soldLongSleeveQ':soldLongSleeveQ,
        'soldBabyOnesieQ':soldBabyOnesieQ,
        'soldMugQ':soldMugQ,
        'soldBagQ':soldBagQ,
        'soldWaterBottleQ':soldWaterBottleQ,
        'countContext': countContext
    }

    return render( request, 'store_index/reports.html', context)

def billing(request):
    return render(request, 'store_index/billing.html')

def orderconfirm(request):
    context = {}
    if request.method == 'POST':
        source = string.digits
        randomOrderNumber=''.join((random.choice(source) for i in range(10)))
        order = Order.objects.get(id=request.POST['order'])
        order.randomOrderNumber = randomOrderNumber
        order.save()
        request.session['orderNo'] = randomOrderNumber
        request.session.get('orderNo', randomOrderNumber)
        context.update({'orderNo': order.randomOrderNumber})
        ops = OrderProduct.objects.filter(Order=order)
        totalQ = 0
        for op in ops:
            q = op.Quantity
            totalQ += q
            
        if totalQ < 5:
            days = 5
        elif totalQ < 12:
            days = 10
        elif totalQ < 20:
            days = 14
        elif totalQ < 30:
            days = 18
        
        cart = cartFunct(request)
        cart = cart['globalCart']
        cart = cart.cart
        cart.delete()
        print(cart)

        return JsonResponse({'orderNo': order.randomOrderNumber, 'days': days})
        
    return render(request, 'store_index/confirmation.html')

def paymenterror(request):
    return render(request, 'store_index/error.html')

def aboutus(request):
    return render(request, 'store_index/aboutus.html')

def contactus(request):
    return render(request, 'store_index/contactus.html')

def turnoff(request):
    if request.method == 'POST':
        checked = request.POST.get('checked')
        if checked == True or checked == 'true':
            request.session['siteDisabled'] = True
            siteDisabledFunct(request, checked)
        elif checked == False or checked == 'false':
            request.session['siteDisabled'] == False
            siteDisabledFunct(request, checked)
    return render(request, 'store_index/turnoff.html')