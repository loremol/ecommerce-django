from django.urls import path

from .views import get_own_orders, delete_order, get_order_details, checkout, update_order

urlpatterns = [
    path('', get_own_orders, name='order-list'),
    path('checkout/', checkout, name='order-list'),
    path('update/<int:pk>/', update_order, name='update-order'),
    path('<int:pk>/', get_order_details, name='order-details'),
    path('cancel/<int:pk>/', delete_order, name='delete-order')
]
