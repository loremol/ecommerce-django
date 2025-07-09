from django.urls import path, include

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('store/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
]
