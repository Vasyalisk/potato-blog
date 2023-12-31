from django.db import models
from rest_framework import serializers

import feedback.models
import posts.models
from users.serializers import UserListSerializer


class CommentListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = feedback.models.Comment
        fields = [
            "id",
            "content",
            "user",
            "likes_count",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="post",
        queryset=posts.models.Post.objects.all(),
    )
    likes_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = feedback.models.Comment
        fields = [
            "id",
            "content",
            "user",
            "post_id",
            "likes_count",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = feedback.models.Comment
        fields = [
            "id",
            "content",
            "user",
            "likes_count",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
        }


class BaseLikeChangeSerializer(serializers.Serializer):
    like_queryset: models.QuerySet = None
    lookup_parent_field: str = None

    is_liked = serializers.BooleanField()

    class Meta:
        fields = [
            "is_liked",
        ]

    def update(self, parent_instance, validated_data):
        action_map = {True: self.add_like, False: self.remove_like}
        # noinspection PyArgumentList
        action_map[validated_data["is_liked"]](parent_instance)

        return validated_data

    def _get_queryset_kwargs(self, parent_instance):
        user = self.context["request"].user
        return {
            "user_id": user.id,
            self.lookup_parent_field: parent_instance.id,
        }

    def add_like(self, parent_instance):
        kwargs = self._get_queryset_kwargs(parent_instance)
        self.like_queryset.get_or_create(**kwargs)

    def remove_like(self, parent_instance):
        kwargs = self._get_queryset_kwargs(parent_instance)
        self.like_queryset.filter(**kwargs).delete()


class PostLikeChangeSerializer(BaseLikeChangeSerializer):
    lookup_parent_field = "post_id"
    like_queryset = feedback.models.PostLike.objects.all()


class CommentLikeChangeSerializer(BaseLikeChangeSerializer):
    lookup_parent_field = "comment_id"
    like_queryset = feedback.models.CommentLike.objects.all()
