from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions

import feedback.filters
import feedback.models
import feedback.permissions
import feedback.serializers
import posts.models
from core.serializers import EmptySerializer
from core.viewsets import ActionViewSet


@extend_schema_view(
    list=extend_schema(
        description=(
            "List and / or filter comments\n\n" "Unless `post_id` is specified, all comments get filtered / shown"
        )
    ),
    create=extend_schema(
        description=(
            "Create new comment\n\n"
            "- Only authorized users can create comments\n\n"
            "- Current authorized user becomes owner of the comment"
        )
    ),
    update=extend_schema(description=("Update comment\n\n" "Only authorized owner can update comment")),
    destroy=extend_schema(description=("Delete comment\n\n" "Only authorized owner can delete comment")),
)
class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ActionViewSet,
):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = feedback.models.Comment.with_likes_count().select_related("user")
    filterset_class = feedback.filters.CommentFilterSet

    action_querysets = {"destroy": feedback.models.Comment.objects.all(), "list": queryset.order_by("-created_at")}
    action_serializers = {
        "list": feedback.serializers.CommentListSerializer,
        "create": feedback.serializers.CommentCreateSerializer,
        "partial_update": feedback.serializers.CommentUpdateSerializer,
        "destroy": EmptySerializer,
    }
    action_permissions = {
        "create": [permissions.IsAuthenticated],
        "partial_update": [permissions.IsAuthenticated, feedback.permissions.IsMyComment],
        "destroy": [permissions.IsAuthenticated, feedback.permissions.IsMyComment],
    }


@extend_schema(
    description=(
        "Like or unlike post\n\n"
        "- Only authorized users can toggle post likes\n\n"
        "- Authorized user can toggle like on own post\n\n"
        "- Each user can leave at most 1 like on the post, e.g. if same user likes post several times, post still has "
        "exactly 1 like from that user\n\n"
    )
)
class PostLikeChangeView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    queryset = posts.models.Post.objects.all().defer("content")
    lookup_url_kwarg = "id"
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = feedback.serializers.PostLikeChangeSerializer


@extend_schema(
    description=(
        "Like or unlike comment\n\n"
        "- Only authorized users can toggle comment likes\n\n"
        "- Authorized user can toggle like on own comment\n\n"
        "- Each user can leave at most 1 like on the comment, e.g. if same user likes comment several times, comment "
        "still has exactly 1 like from that user\n\n"
    )
)
class CommentLikeChange(generics.UpdateAPIView):
    http_method_names = ["patch"]
    queryset = feedback.models.Comment.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "id"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = feedback.serializers.CommentLikeChangeSerializer
