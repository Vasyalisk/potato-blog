from rest_framework import serializers

import posts.models
from users.serializers import UserListSerializer


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

    def validate_name(self, val: str):
        return val.lower()


class PostDetailSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    tags = TagSerializer(many=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "user",
            "tags",
            "likes_count",
        ]


class PostListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    content_short = serializers.CharField()
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content_short",
            "created_at",
            "updated_at",
            "user",
            "likes_count",
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=posts.models.Tag.objects.all(),
        many=True,
        write_only=True
    )
    likes_count = serializers.IntegerField(default=0)

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "user",
            "created_at",
            "updated_at",
            "tag_ids",
            "tags",
            "likes_count",
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
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags",
        queryset=posts.models.Tag.objects.all(),
        many=True,
        write_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    user = UserListSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = posts.models.Post
        fields = [
            "id",
            "title",
            "content",
            "created_at",
            "updated_at",
            "user",
            "tag_ids",
            "tags",
            "likes_count",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            self.update_tags(instance, validated_data.pop("tags"))

        return super().update(instance, validated_data)

    def update_tags(self, instance: posts.models.Post, tags: list[posts.models.Tag]):
        instance.tags.clear()
        instance.tags.add(*tags)
