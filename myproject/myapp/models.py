from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
# from .models import Transaction
from django.conf import settings


class Product(models.Model):
    number = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    pictureURL = models.URLField()
    quantity_on_hand = models.IntegerField(default=100)  # New field with default value

    def __str__(self):
        return self.description


class Transaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    vendor = models.CharField(max_length=100)
    trans = models.CharField(max_length=100)
    cc = models.CharField(max_length=100)  # Credit Card Number
    name = models.CharField(max_length=100)
    exp = models.CharField(max_length=7)  # Expiry Date
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=50)
    authorization = models.CharField(max_length=100)
    timeStamp = models.BigIntegerField()

    def __str__(self):
        return f"{self.name} - {self.trans}"


class CustomerInformation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mailing_address = models.TextField()
    credit_card_info = models.CharField(max_length=255)  # Consider storing only a token or last 4 digits
    quantity = models.IntegerField(default=1)  # New field to store the quantity of the purchase
    shipping_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    handling_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    credit_card_expiration_date = models.DateField(null=True, blank=True)  # Optional date field

    def __str__(self):
        return f"{self.name} - {self.email}"

# class CartItem(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
#     product = models.ForeignKey('Product', to_field='id', on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     customer_information = models.ForeignKey(CustomerInformation, on_delete=models.SET_NULL, null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.product.description} - Quantity: {self.quantity}"
#
#     @property
#     def total_price(self):
#         base_price = self.product.price * self.quantity
#         # Assuming shipping and handling charges should be calculated per item based on the quantity
#         shipping_charge = self.quantity * self.product.weight * 10  # $10 per unit weight
#         handling_charge = 5  # Fixed handling fee
#         return base_price + shipping_charge + handling_charge
#
#     class Meta:
#         ordering = ['product']

# from django.db import models
#
# class CustomerInformation(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     mailing_address = models.TextField()
#     credit_card_info = models.CharField(max_length=255)  # Consider storing only a token or last 4 digits
#     quantity = models.IntegerField(default=1)
#     shipping_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
#     handling_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
#     product_description = models.TextField(default="No description available")
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.name} - {self.email}"
