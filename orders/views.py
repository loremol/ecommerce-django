from decimal import Decimal

from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from cart.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_user_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def checkout(request):
    try:
        # Get the user's cart
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total with discounts
        total_amount = Decimal('0.00')
        order_items_data = []

        for cart_item in cart_items:
            product = cart_item.product
            quantity = cart_item.quantity

            # Check stock availability
            if product.stock_quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use discounted price if available, otherwise use original price
            unit_price = cart_item.discounted_price if cart_item.discounted_price else product.price
            item_total = unit_price * quantity
            total_amount += item_total

            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': item_total
            })

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total=total_amount,
            status='P'
        )

        # Create order items and update product stock
        for item_data in order_items_data:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )

            # Update product stock
            product = item_data['product']
            if not product.reduce_stock(item_data['quantity']):
                return Response(
                    {'error': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )


        # Clear the cart after successful order creation
        cart.items.all().delete()

        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total': float(total_amount)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f'Checkout failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
def delete_order(request, pk):
    order = Order.objects.get(pk=pk)

    if order.user != request.user:
        return Response({'error': 'You do not have permission to delete this order'}, status=status.HTTP_403_FORBIDDEN)

    if order.status != 'P':
        return Response({'error': f'Order #{pk} is not pending and cannot be deleted'}, status=status.HTTP_403_FORBIDDEN)

    for item in order.items.all():
        item.product.increase_stock(item.quantity)

    order.items.all().delete()
    order.delete()
    return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_order_details(request, pk):
    order = Order.objects.get(pk=pk)
    if order.user != request.user:
        return Response({'error': 'You do not have permission to view this order'}, status=status.HTTP_403_FORBIDDEN)
    serializer = OrderItemSerializer(order.items.all(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
