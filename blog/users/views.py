from rest_framework import decorators, generics, mixins, permissions

import users.filters
import users.models
import users.permissions
import users.serializers
from core.viewsets import ActionViewSet


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    ActionViewSet,
):
    queryset = users.models.User.objects.all()
    action_permissions = {
        "partial_update": [permissions.IsAuthenticated, users.permissions.IsMe],
        "me": [permissions.IsAuthenticated],
    }
    action_serializers = {
        "retrieve": users.serializers.UserDetailSerializer,
        "list": users.serializers.UserListSerializer,
        "partial_update": users.serializers.UserUpdateSerializer,
        "me": users.serializers.UserDetailSerializer,
    }
    http_method_names = ["get", "patch"]
    filterset_class = users.filters.UserFilterSet

    @decorators.action(detail=False, filterset_class=None, pagination_class=None)
    def me(self, request, *args, **kwargs):
        self.kwargs["pk"] = self.request.user.id
        return mixins.RetrieveModelMixin.retrieve(self, request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = users.serializers.RegisterSerializer


class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = users.serializers.ChangePasswordSerializer
