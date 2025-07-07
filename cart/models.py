from django.db import models

from accounts.models import CustomUser
from products.models import Product, Category


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name}: {self.quantity}x"


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(CartItem)

    def __str__(self):
        return f"Cart for {self.user}"


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def is_valid(self, date):
        return self.expiry_date > date

    def __str__(self):
        return f"Discount: {self.code} - {self.percentage}%"
