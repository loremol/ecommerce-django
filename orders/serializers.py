from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'date', 'status', 'total']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    paid_price_per_unit = serializers.DecimalField(source='unit_price', max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_price', 'paid_price_per_unit', 'quantity', 'total_price']
