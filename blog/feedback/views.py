from core.viewsets import ActionViewSet
from rest_framework import mixins, permissions, generics
import feedback.models
import feedback.serializers
import feedback.permissions
import feedback.filters
import posts.models


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ActionViewSet,
):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = feedback.models.Comment.objects.all().select_related("user")
    filterset_class = feedback.filters.CommentFilterSet

    action_querysets = {
        "destroy": feedback.models.Comment.objects.all(),
    }
    action_serializers = {
        "list": feedback.serializers.CommentListSerializer,
        "create": feedback.serializers.CommentCreateSerializer,
        "partial_update": feedback.serializers.CommentUpdateSerializer,
    }
    action_permissions = {
        "create": [permissions.IsAuthenticated],
        "partial_update": [permissions.IsAuthenticated, feedback.permissions.IsMyComment],
        "destroy": [permissions.IsAuthenticated, feedback.permissions.IsMyComment],
    }


class PostLikeChangeView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    queryset = posts.models.Post.objects.all().defer("content")
    lookup_url_kwarg = "id"
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = feedback.serializers.PostLikeChangeSerializer


class CommentLikeChange(generics.UpdateAPIView):
    http_method_names = ["patch"]
    queryset = feedback.models.Comment.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "id"
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = feedback.serializers.CommentLikeChangeSerializer