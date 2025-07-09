from django.urls import path

from products import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.create_category, name='category-create'),
    path('categories/update/<int:pk>/', views.update_category, name='update-category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete-category'),

    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.create_product, name='product-create'),
    path('products/update/<int:pk>/', views.update_product, name='update-product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete-product'),
]
