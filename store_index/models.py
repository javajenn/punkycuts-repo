from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.urls import reverse 
from django.utils.text import slugify

# Create your models here.
class State(models.Model):
    State = models.CharField(max_length=20)
    def __str__(self):
        return self.State

class Customer(models.Model):
    User = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    FirstName = models.CharField(max_length=20, null=False, blank=False, default='')
    LastName = models.CharField(max_length=20, null=False, blank=False, default='')

    Email = models.CharField(max_length=50, null=False, blank=False, default='', unique=True)
    PhoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    PhoneNumber = models.CharField(max_length = 15, null=False, blank=True, default='')

    ShippingAddress = models.CharField(max_length=100, null=False, blank=True, default='')
    ShippingCity = models.CharField(max_length=50, null=False, blank=True, default='')
    ShippingZipCode = models.CharField(max_length=5, null=False, blank=True, default='')
    ShippingState = models.ForeignKey(State, related_name="ShippingState", on_delete=models.CASCADE, null=True, blank=True, default=None)

    BillingAddress = models.CharField(max_length=100, null=False, blank=True, default='')
    BillingCity = models.CharField(max_length=50, null=False, blank=True, default='')
    BillingZipCode = models.CharField(max_length=5, null=False, blank=True, default='')
    BillingState = models.ForeignKey(State, related_name="BillingState", on_delete=models.CASCADE, null=True, blank=True, default=None)

    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.FirstName + " " + self.LastName

class Category(models.Model):
  Name = models.CharField(max_length=100)
  Description = models.CharField(max_length=100)

  def __str__(self):
    return self.category_name

  class Meta:
     verbose_name_plural="category"

class Status(models.Model):
  Description = models.CharField(max_length=100)
  
  def __str__(self):
    return f"{self.status_description}"

  class Meta:
  #  db_table = 'products_status'
    verbose_name_plural='status'

class Order(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    Date = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.id

class Type(models.Model):
  Product_Type = models.CharField(max_length=100)

  def str(self):
    return f"{self.product_type}"

  class Meta:
    verbose_name_plural='type'

class Product(models.Model):
    Name = models.CharField(max_length=50)
    Description = models.CharField(max_length=100)
    #statusID = models.IntegerField()
    Status = models.ForeignKey(Status, on_delete= models.CASCADE, related_name="products", default='')
    Price = models.DecimalField(max_digits=5, decimal_places=2)
    Quantity = models.IntegerField()
    Type = models.ForeignKey(Type, on_delete=models.CASCADE, default='')
    Slug = models.SlugField(default="", blank=True, null=False, db_index=True) #T-shirt-1 => t-shirt-1
    Product_Categories = models.ManyToManyField(Category)

    def get_absolute_url(self):
      return reverse("product-detail", args=[self.slug])

     #  def save(self, *args, **kwargs):
     #   self.slug = slugify(self.productName)  ##?productName ? title
     #  super().save(*args, **kwargs)

    def __str__(self):
      # return f"{self.productName} ({self.productDescription}) ({self.statusID}) ({self.price}) ({self.quantity}) ({self.productTypeID})"
        return f"{self.productName} ({self.productDescription}) ({self.status}) ({self.price}) ({self.quantity}) ({self.product_categories})"

    class Meta:
    # db_table = 'products_product'
     #verbose_name="product"
     verbose_name_plural="product"

class OrderProduct(models.Model):
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)

class Cart(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    Quantity = models.IntegerField(default=None)
    Price = models.IntegerField(default=None)

class Image(models.Model):
    FileName = models.CharField(max_length=50, null=False, blank=False)
    Picture = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)
    DateAdded = models.DateTimeField(auto_now=False, auto_created=True, editable=False)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)

class Screenshot(models.Model):
    screenshot = models.ImageField(upload_to='img/screenshots/', help_text='Html2canvas screenshot')