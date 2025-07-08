from django.urls import path

from . import views
from .views import ListUsersView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('ban/', views.ban_user, name='ban_user'),
    path('unban/', views.unban_user, name='unban_user'),
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('users/<int:pk>/', views.get_user, name='user_detail'),
]
