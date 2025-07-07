from rest_framework import serializers
from cart.models import CartItem, Cart
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Include full product details
    quantity = serializers.IntegerField()
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, default=product['price'])
    discount_applied = serializers.BooleanField(default=False)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'discounted_price', 'discount_applied', 'total_price']

    def get_total_price(self, obj):
        # Use discounted price if available, otherwise use original price
        price = obj.discounted_price if obj.discounted_price else obj.product.price
        return price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    original_total = serializers.SerializerMethodField()
    total_savings = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_amount', 'original_total', 'total_savings']

    def get_total_amount(self, obj):
        # Calculate total using discounted prices
        total = 0
        for item in obj.items.all():
            price = item.discounted_price if item.discounted_price else item.product.price
            total += price * item.quantity
        return total

    def get_original_total(self, obj):
        # Calculate original total without discounts
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_total_savings(self, obj):
        # Calculate total savings
        original = self.get_original_total(obj)
        discounted = self.get_total_amount(obj)
        return original - discounted