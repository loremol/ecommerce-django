from django.urls import path

from .views import get_own_orders, delete_order, get_order_details, checkout, update_order, get_all_orders, \
    get_statistics

urlpatterns = [
    path('all/', get_all_orders, name='all-orders'),  # Add this line
    path('', get_own_orders, name='order-list'),
    path('<int:pk>/', get_order_details, name='order-details'),
    path('checkout/', checkout, name='order-list'),
    path('update/<int:pk>/', update_order, name='update-order'),
    path('cancel/<int:pk>/', delete_order, name='delete-order'),
    path('stats/', get_statistics, name='get-statistics')
]
