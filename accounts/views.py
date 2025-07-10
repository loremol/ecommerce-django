from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models.functions import datetime
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from products.permissions import IsModerator
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer


@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key},
            status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
@authentication_classes([TokenAuthentication])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)



class ListUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsModerator]
    authentication_classes = [TokenAuthentication]


@api_view(['GET'])
@login_required
@authentication_classes([TokenAuthentication])
@permission_classes([IsModerator])
def get_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    if not user:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(UserSerializer(user).data)


@api_view(['GET'])
@login_required
@authentication_classes([TokenAuthentication])
def get_own_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@login_required
@authentication_classes([TokenAuthentication])
def update_user(request):
    user = request.user

    # Get the data from request
    username = request.data.get('username')
    email = request.data.get('email')
    phone = request.data.get('phone', '')
    address = request.data.get('address', '')
    date_of_birth = request.data.get('date_of_birth')

    # Validate required fields
    if not username or not email:
        return Response({'error': 'Username and email are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username is already taken by another user
    if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email is already taken by another user
    if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user.username = username
    user.email = email
    user.phone = phone
    user.address = address

    if date_of_birth:
        user.date_of_birth = date_of_birth

    user.save()

    return Response({
        'message': 'User updated successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@login_required
@authentication_classes([TokenAuthentication])
@permission_classes([IsModerator])
def ban_user(request):
    username = request.data.get('username')

    if not username:
        return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)

    user_to_ban = CustomUser.objects.get(username=username)
    if not user_to_ban:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user == user_to_ban:
        return Response({'error': 'You cannot ban yourself.'}, status=status.HTTP_403_FORBIDDEN)

    if not request.user.is_staff and user_to_ban.is_staff:
        return Response({'error': 'You cannot ban an Admin.'}, status=status.HTTP_403_FORBIDDEN)

    user_to_ban.is_banned = True
    user_to_ban.updated_at = datetime.datetime.now()
    user_to_ban.save()

    return Response({'message': f'User {username} banned successfully'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@login_required
@authentication_classes([TokenAuthentication])
@permission_classes([IsModerator])
def unban_user(request):
    username = request.data.get('username')
    if not username:
        return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)
    user_to_unban = CustomUser.objects.get(username=username)
    if not user_to_unban:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user == user_to_unban:
        return Response({'error': 'You cannot unban yourself.'}, status=status.HTTP_403_FORBIDDEN)

    if not request.user.is_staff and user_to_unban.is_staff:
        return Response({'error': 'You cannot unban an Admin.'}, status=status.HTTP_403_FORBIDDEN)

    user_to_unban.is_banned = False
    user_to_unban.updated_at = datetime.datetime.now()
    user_to_unban.save()
    return Response({'message': f'User {username} unbanned successfully'}, status=status.HTTP_200_OK)


