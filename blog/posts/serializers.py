from rest_framework import serializers
import posts.models
from users.serializers import UserListSerializer


class PostDetailSerializer(serializers.ModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "user",
        ]


class PostListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    content_short = serializers.CharField()

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content_short",
            "created_at",
            "updated_at",
            "user",
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "user",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "user",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "user": {"read_only": True},
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = posts.models.Tag
        fields = [
            "id",
            "name",
            "created_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
        }
