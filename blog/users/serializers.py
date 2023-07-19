import users.models
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method


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
        extra_kwargs = {
            "id": {"read_only": True}
        }
