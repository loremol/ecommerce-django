from django.urls import path

from .views import get_user_orders, delete_order, get_order_details, checkout

urlpatterns = [
    path('', get_user_orders, name='order-list'),
    path('checkout/', checkout, name='order-list'),
    path('<int:pk>/', get_order_details, name='order-details'),
    path('cancel/<int:pk>/', delete_order, name='delete-order')
]
