from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'address', 'date_of_birth']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if user.is_banned:
                raise serializers.ValidationError('Account is banned')

        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, allow_blank=True)
    password = serializers.CharField(write_only=True, allow_blank=True)
    phone = serializers.CharField(max_length=15, allow_blank=True)
    address = serializers.CharField(max_length=255, allow_blank=True)
    date_of_birth = serializers.DateField(allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'address', 'date_of_birth']
        read_only_fields = ['id', 'created_at']
