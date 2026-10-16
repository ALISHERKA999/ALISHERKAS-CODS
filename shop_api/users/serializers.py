
import secrets

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import ConfirmationCode
from .validators import validate_phone_number

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["birthdate"] = (
            user.birthdate.isoformat()
            if user.birthdate
            else None
        )
        return token
    
User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return value

    def validate_phone_number(self, value):
        try:
            validate_phone_number(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_active=False
        )

        code = str(secrets.randbelow(900000) + 100000)

        ConfirmationCode.objects.create(
            user=user,
            code=code
        )

        return user


class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(
                email__iexact=attrs['email']
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Пользователь не найден.'
            )

        try:
            confirmation = user.confirmation_code
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError(
                'Код подтверждения не найден.'
            )

        if not secrets.compare_digest(
            confirmation.code,
            attrs['code']
        ):
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )

        attrs['user'] = user
        return attrs

    @transaction.atomic
    def save(self):
        user = self.validated_data['user']
        user.is_active = True
        user.save(update_fields=['is_active'])
        ConfirmationCode.objects.filter(user=user).delete()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs['email'].strip().lower(),
            password=attrs['password']
        )

        if user is None:
            raise serializers.ValidationError(
                'Неверный email или пароль.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Аккаунт не подтверждён.'
            )

        attrs['user'] = user
        return attrs

    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["birthdate"] = (
            user.birthdate.isoformat()
            if user.birthdate
            else None
        )
        return token

