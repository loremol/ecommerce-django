from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_cart, name='cart-detail'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
    path('apply_discount/', views.apply_discount, name='apply-discount')
]
