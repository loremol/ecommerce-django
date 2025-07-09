from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_cart, name='cart-detail'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
    path('create_discount/', views.create_discount, name='create-discount'),
    path('apply_discount/', views.apply_discount, name='apply-discount'),
    path('delete_discount/<int:pk>/', views.delete_discount, name='delete-discount'),
    path('discounts/', views.get_discounts, name='get-discounts')
]
