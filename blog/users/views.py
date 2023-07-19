from core.viewsets import ActionViewSet
from rest_framework import mixins, permissions
import users.models
import users.permissions
import users.serializers
import users.filters


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    ActionViewSet,
):
    queryset = users.models.User.objects.all()
    action_permissions = {
        "partial_update": [permissions.IsAuthenticated, users.permissions.IsMe]
    }
    action_serializers = {
        "retrieve": users.serializers.UserDetailSerializer,
        "list": users.serializers.UserListSerializer,
        "partial_update": users.serializers.UserUpdateSerializer,
    }
    http_method_names = ["get", "patch"]
    filterset_class = users.filters.UserFilterSet
