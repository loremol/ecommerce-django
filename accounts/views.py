from django.contrib.auth import login, logout
from django.db.models.functions import datetime
from rest_framework import permissions, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from products.permissions import IsModerator
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
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
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        if user.is_banned:
            return Response({'error': 'User is banned'}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        response = Response({
            'user': UserSerializer(user).data,
            'token': token.key},
            status=status.HTTP_200_OK)
        response.set_cookie(
            'auth_token',
            value=token.key,
            httponly=True,
            secure=True,
            max_age=3600,
            samesite='None',
        )
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    # request.user.auth_token.delete()
    logout(request)
    return Response({'message': 'Logged out successfully'})


@permission_classes([IsModerator])
class ListUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
@permission_classes([IsModerator])
def get_user(request, pk):
    user = CustomUser.objects.get(pk=pk)
    if not user:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([IsModerator])
def ban_user(request):
    username = request.data.get('username')

    if not username:
        return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.get(username=username)
    if not user:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user == user:
        return Response({'error': 'You cannot ban yourself.'}, status=status.HTTP_403_FORBIDDEN)

    user.is_banned = True
    user.updated_at = datetime.datetime.now()
    user.save()

    return Response({'message': f'User {username} banned successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsModerator])
def unban_user(request):
    username = request.data.get('username')
    if not username:
        return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)
    user = CustomUser.objects.get(username=username)
    if not user:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    if request.user == user:
        return Response({'error': 'You cannot unban yourself.'}, status=status.HTTP_403_FORBIDDEN)
    user.is_banned = False
    user.updated_at = datetime.datetime.now()
    user.save()
    return Response({'message': f'User {username} unbanned successfully'}, status=status.HTTP_200_OK)
