from django.db import models

from accounts.models import CustomUser
from products.models import Product

# Collection of OrderItems
class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

# Some quantity of one specific product
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order accounting discounts
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # unit_price * quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order #{self.order.id})"

    def save(self, *args, **kwargs):
        # Calculate total_price if not provided
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

