from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

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

    @swagger_serializer_method(serializers.BooleanField())
    def get_is_me(self, user):
        return self.context["request"].user == user

    @swagger_serializer_method(serializers.EmailField(allow_null=True))
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
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    class Meta:
        model = users.models.User
        fields = [
            "username",
            "email",
            "password",
            "access_token",
            "refresh_token",
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

    def get_access_token(self, user):
        return str(self.context["token"].access_token)

    def get_refresh_token(self, user):
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
