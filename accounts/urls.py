from django.urls import path

from . import views
from .views import ListUsersView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.get_own_profile, name='profile'),
    path('update/', views.update_user, name='update_user'),
    path('ban/', views.ban_user, name='ban_user'),
    path('unban/', views.unban_user, name='unban_user'),
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('users/<int:pk>/', views.get_user, name='user_detail'),
]
