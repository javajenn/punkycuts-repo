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
    path('products/', views.products, name="products"),
    path('small-business-spotlight/', views.smallbusiness, name="smallbusiness")
]