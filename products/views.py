from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer, SimpleProductSerializer


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_product(request):
    serializer = SimpleProductSerializer(data=request.data) # Using a different serializer that doesn't require Category object but only its id
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([permissions.IsAdminUser])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


