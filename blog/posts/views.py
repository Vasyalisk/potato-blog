from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, viewsets

import posts.filters
import posts.models
import posts.permissions
import posts.serializers
from core.serializers import EmptySerializer
from core.viewsets import ActionViewSet


@extend_schema_view(
    retrieve=extend_schema(description=("Get detailed post info")),
    partial_update=extend_schema(description=("Update post\n\n" "Only authorized owner has permission to update post")),
    list=extend_schema(description=("List and / or filter posts")),
    create=extend_schema(description=("Create new post\n\n" "Current authorized user becomes owner of the post")),
    destroy=extend_schema(description=("Delete post\n\n" "Only authorized owner has permission to delete post")),
)
class PostViewSet(ActionViewSet, viewsets.ModelViewSet):
    queryset = posts.models.Post.objects.with_likes_count().select_related("user")

    action_serializers = {
        "retrieve": posts.serializers.PostDetailSerializer,
        "partial_update": posts.serializers.PostUpdateSerializer,
        "list": posts.serializers.PostListSerializer,
        "create": posts.serializers.PostCreateSerializer,
        "destroy": EmptySerializer,
    }
    action_permissions = {
        "partial_update": [permissions.IsAuthenticated, posts.permissions.IsMyPost],
        "create": [permissions.IsAuthenticated],
        "destroy": [permissions.IsAuthenticated, posts.permissions.IsMyPost],
    }
    action_querysets = {
        "list": queryset.with_content_short().defer("content").order_by("-created_at"),
        "destroy": posts.models.Post.objects.all(),
    }

    http_method_names = ["get", "post", "patch", "delete"]
    filterset_class = posts.filters.PostFilterSet


@extend_schema_view(
    list=extend_schema(description=("List and / or filter tags")),
    create=extend_schema(
        description=(
            "Create new tag\n\n"
            "- Each tag should have unique name\n\n"
            "- Tag name gets converted to lower-case\n\n"
            "- Only authorized users can create new tags"
        )
    ),
)
class TagViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    ActionViewSet,
):
    queryset = posts.models.Tag.objects.all().order_by("name")
    serializer_class = posts.serializers.TagSerializer
    filterset_class = posts.filters.TagFilterSet
    action_permissions = {
        "create": [permissions.IsAuthenticated],
    }
