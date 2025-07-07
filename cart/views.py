from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem, Discount
from cart.serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartListView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        serializer = CartItemSerializer(cart_items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve cart items'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartItemSerializer(data=request.data)
    if serializer.is_valid():
        product_id = request.data.get('product')

        if not product_id:
            return Response({'error': 'Product ID is missing'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)

        quantity = serializer.validated_data['quantity']

        if product.stock_quantity < quantity:
            return Response({
                'error': f'Cannot add {quantity} items to the cart. Only {product.stock_quantity} items are available.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the product is already in the cart
        existing_cart_item = cart.items.filter(product=product).first()

        if existing_cart_item:
            # Update quantity if item already exists
            new_quantity = existing_cart_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                return Response({
                    'error': f'Cannot add {quantity} more items. Only {product.stock_quantity - existing_cart_item.quantity} items can be added.'
                }, status=status.HTTP_400_BAD_REQUEST)
            existing_cart_item.quantity = new_quantity
            existing_cart_item.save()
        else:
            # Create new cart item and add to cart
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                discounted_price=product.price
            )
            cart.items.add(cart_item)

        cart.save()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()

    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_discount(request):
    cart = get_object_or_404(Cart, user=request.user)
    discount_code = request.data.get('discount_code')
    if discount_code:
        # Apply the discount to the cart
        discount = get_object_or_404(Discount, code=discount_code)
        for item in cart.items.all():
            if item.product.category == discount.category and item.discount_applied == False:
                item.discounted_price = item.product.price - item.product.price * (discount.percentage / 100)
                item.discount_applied = True
                item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    else:
        return Response({'error': 'Discount code not provided'}, status=status.HTTP_400_BAD_REQUEST)
