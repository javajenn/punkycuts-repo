from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('customize', views.customize, name="customize"),
    # path('api/save_screenshot', views.saveScreenshot.as_view(), name='save-screenshot')
    path('profile', views.profile, name='profile'),
    #path('customers/', views.CustomerListView.as_view(), name='customers'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate_user, name='activate'),
    path('api/sms/', views.handle_sms, name="sendsms"),
    path('products/', views.products, name='products'),
    path('products/<slug:cat>', views.products, name='products'),
    path('products/details/<slug:slug>', views.product_details, name='product_details'),
    path('small-business-spotlight/', views.smallbusiness, name="smallbusiness"),
    path('checkout/shipping', views.checkout_shipping, name='checkout_shipping'),
    path('checkout/billing/<str:customer_id>', views.checkout_billing, name='checkout_billing'),
    path('checkout/complete', views.checkout_complete, name='checkout_complete'),
    path('handlecart/', views.handle_cart, name='handlecart'),
    path('punkydashboard/', views.punkydashboard, name='punkydashboard'),
    path('newsletter/signup/', views.NewsletterSignUp, name='news_signup'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribe, name='news_unsub'),
    path('newsletter/write/', views.ControlNewsletter, name='news_write'),
    path('checkout/', views.checkout, name='checkout'),
    path('reports/', views.financial, name='reports'),
    path('checkout/billing/', views.billing, name='billing'),
    path('checkout/confirmation/', views.orderconfirm, name='confirmation'),
    path('checkout/error/', views.paymenterror, name='paymenterror')
]