from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models.fields.related import ForeignKey
from django.urls import reverse 
from django.utils.text import slugify
from datetime import datetime

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

    #Properties
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.FirstName + " " + self.LastName

    def save(self, *args, **kwargs):
      phone = self.PhoneNumber
      phone = phone.replace(' ', '')
      phone = phone.replace('(', '')
      phone = phone.replace(')', '')
      phone = phone.replace('-', '')
      phone = '(' + phone[0:3] + ') ' + phone[3:6] + '-' + phone[6:10]
      self.PhoneNumber = phone
      super(Customer, self).save(*args, **kwargs)

class Category(models.Model):
  Name = models.CharField(max_length=100)
  Description = models.CharField(max_length=100)
  slug = models.SlugField(default="", blank=True, null=False, db_index=True)

  def save(self, *args, **kwargs):
    self.slug = slugify(self.Name)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.Name

  class Meta:
     verbose_name_plural="category"

class Status(models.Model):
  Description = models.CharField(max_length=100)
  
  def __str__(self):
    return f"{self.Description}"

  class Meta:
  #  db_table = 'products_status'
    verbose_name_plural='status'

class Order(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    Date = models.DateTimeField(default=datetime.now, blank=True)
    Total = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    RandomOrderNumber = models.CharField(max_length=10, default='')
    #(auto_now=False, auto_now_add=False)
    def __str__(self):
        return str("ORDERID: " + str(self.id) + " CUSTOMER: " + str(self.Customer) + " AMT PAID: " + str(self.Total))

class Size(models.Model):
  Product_Size = models.CharField(max_length=20)
  def __str__(self):
    return self.Product_Size

class Type(models.Model):
  Product_Type = models.CharField(max_length=100)
  Type_Size = models.ManyToManyField(Size, blank=True)

  def __str__(self):
    return f"{self.Product_Type}"

  class Meta:
    verbose_name_plural='type'

class Product(models.Model):
    Name = models.CharField(max_length=50)
    Description = models.CharField(max_length=100)
    #statusID = models.IntegerField()
    Status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name="products", default='')
    Price = models.DecimalField(max_digits=5, decimal_places=2)
    #Quantity = models.IntegerField()
    Type = models.ForeignKey(Type, on_delete=models.CASCADE, default='')
    slug = models.SlugField(default="", blank=True, null=False, db_index=True) #T-shirt-1 => t-shirt-1
    Product_Categories = models.ManyToManyField(Category)
    #Order = models.ManyToManyField(Order)
    Sizes = models.ManyToManyField(Size, blank=True)
    #Color = ?
    def save(self, *args, **kwargs):
      self.slug = slugify(self.Name)
      super().save(*args, **kwargs)

    def get_absolute_url(self):
      return reverse("product-detail", args=[self.slug])

     #  def save(self, *args, **kwargs):
     #   self.slug = slugify(self.productName)  ##?productName ? title
     #  super().save(*args, **kwargs)

    def __str__(self):
      # return f"{self.productName} ({self.productDescription}) ({self.statusID}) ({self.price}) ({self.quantity}) ({self.productTypeID})"
        return f"{self.Name}"

    class Meta:
    # db_table = 'products_product'
     #verbose_name="product"
     verbose_name_plural="product"

class OrderProduct(models.Model):
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    Price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    Quantity = models.PositiveIntegerField(default=1)
    Size = ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    #Subtotal = models.
    def __str__(self):
      return f"ORDERID: {self.Order.id} PRODUCT: {self.Product}"

    def save(self, *args, **kwargs):
      self.Price =  self.Product.Price * self.Quantity
      super().save(*args, **kwargs)

# class Cart(models.Model):
#     Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
#     Quantity = models.IntegerField(default=None)
#     Price = models.IntegerField(default=None)

class Image(models.Model):
    FileName = models.CharField(max_length=50, null=False, blank=False)
    Picture = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)
    DateAdded = models.DateTimeField(auto_now=True, auto_created=True, editable=False)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    def __str__(self):
      return f"{self.FileName}"

class Screenshot(models.Model):
    screenshot = models.ImageField(upload_to='img/screenshots/', help_text='Html2canvas screenshot')

# Newsletter Users Class
class NewsletterUser(models.Model):
    # Subsciption Date
    DateSubscribed = models.DateTimeField(auto_now_add=True)
    DateSubscribedString = str(DateSubscribed)

    # Foreign Keys
    #Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=true)
    SubscriberEmail = models.EmailField(max_length=50, default=None)

    # Returns
    def __str__(self):
        return self.SubscriberEmail

# Newsletter Class
class Newsletter(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Published', 'Published')
    )

    Subject = models.CharField(max_length=250)
    Body = models.TextField()
    Email = models.ManyToManyField(NewsletterUser)
    Status = models.CharField(max_length=10, choices=EMAIL_STATUS_CHOICES)
    DateCreated = models.DateTimeField(auto_now_add=True)
    DateUpdated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="", blank=True, null=False, db_index=True)

    def save(self, *args, **kwargs):
      self.slug = slugify(self.Subject)
      super().save(*args, **kwargs)

    # Returns
    def __str__(self):
        return self.Subject

# Cart Class
class Cart(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    Count = models.PositiveIntegerField(default=0)
    Subtotal = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    Order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    Session = models.CharField(max_length=100, null=True)
    def str(self):
        return "Welcome, {}. You have {} items in your cart. Subtotal: {}".format(self.Customer, self.Count, self.Subtotal)

# Cart Product Class
class CartProduct(models.Model):
  Product = models.ForeignKey(Product, on_delete=models.CASCADE)
  Cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
  Quantity = models.PositiveIntegerField()
  Size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
  def __str__(self):
    return str(self.Product.Name + ': ' + str(self.Quantity))

class Inventory(models.Model):
  Product = models.ForeignKey(Product, on_delete=models.CASCADE)
  Size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
  Quantity = models.PositiveIntegerField()
  def __str__(self):
    return f"PRODUCT: {self.Product} SIZE: {self.Size} QUANTITY: {self.Quantity}"