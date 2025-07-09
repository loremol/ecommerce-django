from decimal import Decimal

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cart.models import Cart
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_own_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def checkout(request):
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


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
def update_order(request, pk):
    order = Order.objects.get(pk=pk)
    if order.user != request.user and not request.user.is_staff:
        return Response(
            {'error': 'You do not have permission to update this order'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get the order status requested from request data
    new_status = request.data.get('status')
    if not new_status:
        return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate status against available choices
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Valid choices are: {", ".join(valid_statuses)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Business logic for status transitions
    current_status = order.status

    # HANDLING OF BAD REQUESTS
    # Regular users can only cancel pending orders
    if not request.user.is_staff:
        if new_status != 'C':
            return Response(
                {'error': 'You can only cancel your orders'},
                status=status.HTTP_403_FORBIDDEN
            )
        if current_status != 'P':
            return Response(
                {'error': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Admin-specific status transition rules
    if request.user.is_staff:
        # Prevent certain invalid transitions
        if current_status == 'C' and new_status != 'P':
            return Response(
                {'error': 'Cancelled orders can only be changed back to Pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if current_status == 'D':
            return Response(
                {'error': 'Delivered orders cannot be modified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if current_status == 'S' and new_status == 'P':
            return Response(
                {'error': 'Shipped orders cannot be changed back to Pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
    # END OF HANDLING OF BAD REQUESTS

    # Handle stock adjustments when cancelling an order
    if current_status != 'C' and new_status == 'C':
        # Restore stock for all items in the order
        for item in order.items.all():
            item.product.increase_stock(item.quantity)

    # Handle stock adjustments when un-cancelling an order (admin only)
    if current_status == 'C' and new_status == 'P' and request.user.is_staff:
        # Check if we have enough stock to un-cancel
        for item in order.items.all():
            if item.product.stock_quantity < item.quantity:
                return Response(
                    {'error': f'Insufficient stock for {item.product.name} to restore order'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Reduce stock for all items
        for item in order.items.all():
            item.product.reduce_stock(item.quantity)

    # Update the status
    order.status = new_status
    order.save()

    # Serialize and return the updated order
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def delete_order(request, pk):
    order = Order.objects.get(pk=pk)

    if order.status != 'P' or order.status != 'C':
        return Response({'error': f'Order #{pk} is not pending or cancelled and cannot be deleted'},
                        status=status.HTTP_403_FORBIDDEN)

    for item in order.items.all():
        item.product.increase_stock(item.quantity)

    order.items.all().delete()
    order.delete()
    return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def get_order_details(request, pk):
    order = Order.objects.get(pk=pk)
    # Allow order owner and admin to GET it
    if order.user != request.user and not request.user.is_staff:
        return Response({'error': 'You do not have permission to view this order'}, status=status.HTTP_403_FORBIDDEN)
    serializer = OrderItemSerializer(order.items.all(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
