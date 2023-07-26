from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema_field
from django_rest_passwordreset.serializers import PasswordValidateMixin

import users.models


class UserDetailSerializer(serializers.ModelSerializer):
    is_me = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = users.models.User
        fields = [
            "id",
            "username",
            "is_me",
            "email",
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_is_me(self, user):
        return self.context["request"].user == user

    @extend_schema_field(serializers.EmailField(allow_null=True))
    def get_email(self, user):
        is_me = self.get_is_me(user)

        if not is_me:
            return None

        return user.email


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = users.models.User
        fields = [
            "id",
            "username",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = users.models.User
        fields = [
            "id",
            "username",
            "email",
        ]
        extra_kwargs = {"id": {"read_only": True}}


class RegisterSerializer(serializers.ModelSerializer):
    access = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()

    class Meta:
        model = users.models.User
        fields = [
            "username",
            "email",
            "password",
            "access",
            "refresh",
        ]
        extra_kwargs = {
            "username": {"write_only": True},
            "email": {"write_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = users.models.User.objects.create_user(**validated_data)
        self.context["token"] = RefreshToken.for_user(user)
        return user

    @extend_schema_field(serializers.CharField())
    def get_access(self, user):
        return str(self.context["token"].access_token)

    @extend_schema_field(serializers.CharField())
    def get_refresh(self, user):
        return str(self.context["token"])


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    status = serializers.CharField(read_only=True, default="OK")

    class Meta:
        fields = [
            "old_password",
            "new_password",
        ]

    def create(self, validated_data):
        kwargs = {
            "username": self.context["request"].user.username,
            "password": validated_data["old_password"],
        }
        user = authenticate(**kwargs)

        if user is None:
            raise serializers.ValidationError({"old_password": "Invalid password"})

        try:
            validate_password(validated_data["new_password"], user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        user.password = make_password(validated_data["new_password"])
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    status = serializers.CharField(read_only=True, default="Ok")


class ResetPasswordConfirmSerializer(PasswordValidateMixin, serializers.Serializer):
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, write_only=True)
    token = serializers.CharField(write_only=True)
    status = serializers.CharField(read_only=True, default="Ok")
