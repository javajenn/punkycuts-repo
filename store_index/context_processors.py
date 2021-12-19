from .models import *
from django.db.models import Q

def cartFunct(request):
    runningtotal = 0
    cartsession = request.session.session_key
    try:
        globalCart = CartProduct.objects.filter(Q(Cart__Session=cartsession))
        cart = Cart.objects.get(Session=cartsession)
        if not globalCart:
            globalCart = None
        else:
            for cp in globalCart:
                cpsub = float(cp.Quantity) * float(cp.Product.Price)
                cp.Subtotal = format(cpsub, '.2f')
                cp.save()
                runningtotal += cpsub
                cart.Subtotal = format(runningtotal, '.2f')
                cart.save()
                globalCart.cart = cart
                try:
                    cp.images = Image.objects.filter(Product_id=cp.Product.id)
                except Image.DoesNotExist:
                    cp.image = None
                #p.images = p.Product.image_set 
    except (CartProduct.DoesNotExist, Cart.DoesNotExist) as e:
        globalCart = None
    return {'globalCart': globalCart}

def maxQuantityPerProduct(request):
    request.maxPerProduct = [1,2,3,4,5,6,7,8,9,10,11,12]
    return {'maxPerProduct': [1,2,3,4,5,6,7,8,9,10,11,12]}

# def updateMessages(request):
#     print(request._messages)
#     return {'msgs': request._messages}

def siteDisabledFunct(request):
    status = request.session.get('siteDisabled')
    if status == True or status == 'true':
        siteDisabled = True
    elif status == False or status == 'false':
        siteDisabled = False
    else:
        siteDisabled = 'Unknown'
    return {'siteDisabed': siteDisabled}