from core.viewsets import ActionViewSet
from rest_framework import viewsets, mixins, permissions
import posts.serializers
import posts.permissions
import posts.models
import posts.filters


class PostViewSet(ActionViewSet, viewsets.ModelViewSet):
    queryset = posts.models.Post.objects.all().select_related("user")

    action_serializers = {
        "retrieve": posts.serializers.PostDetailSerializer,
        "partial_update": posts.serializers.PostUpdateSerializer,
        "list": posts.serializers.PostListSerializer,
        "create": posts.serializers.PostCreateSerializer,
    }
    action_permissions = {
        "partial_update": [permissions.IsAuthenticated, posts.permissions.IsMyPost],
        "create": [permissions.IsAuthenticated],
        "destroy": [permissions.IsAuthenticated, posts.permissions.IsMyPost],
    }
    action_querysets = {
        "list": posts.models.Post.with_content_short(queryset).defer("content"),
        "destroy": posts.models.Post.objects.all(),
    }

    http_method_names = ["get", "post", "patch", "delete"]
    filterset_class = posts.filters.PostFilterSet


class TagViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    ActionViewSet,
):
    queryset = posts.models.Tag.objects.all()
    serializer_class = posts.serializers.TagSerializer
    action_permissions = {
        "create": [permissions.IsAuthenticated],
    }
