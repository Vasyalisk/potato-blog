from django_rest_passwordreset.views import ResetPasswordConfirm, ResetPasswordRequestToken
from rest_framework import decorators, generics, mixins, permissions

import users.filters
import users.models
import users.serializers
from core.viewsets import ActionViewSet


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    ActionViewSet,
):
    queryset = users.models.User.objects.all()
    action_permissions = {
        "me": [permissions.IsAuthenticated],
        "update_me": [permissions.IsAuthenticated],
    }
    action_serializers = {
        "retrieve": users.serializers.UserDetailSerializer,
        "list": users.serializers.UserListSerializer,
        "me": users.serializers.UserDetailSerializer,
        "update_me": users.serializers.UserUpdateSerializer,
    }
    action_querysets = {
        "list": queryset.order_by("username"),
    }
    filterset_class = users.filters.UserFilterSet
    http_method_names = ["get", "patch"]

    @decorators.action(methods=["GET"], detail=False, filterset_class=None, pagination_class=None)
    def me(self, request, *args, **kwargs):
        self.kwargs["pk"] = self.request.user.id
        return mixins.RetrieveModelMixin.retrieve(self, request, *args, **kwargs)

    @me.mapping.patch
    def update_me(self, request, *args, **kwargs):
        self.kwargs["pk"] = self.request.user.id
        return mixins.UpdateModelMixin.partial_update(self, request, *args, **kwargs)

    # Workaround to use UpdateModelMixin in custom action without exposing {basename}/{pk}/ PATCH API
    update = mixins.UpdateModelMixin.update
    perform_update = mixins.UpdateModelMixin.perform_update


class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = users.serializers.RegisterSerializer


class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = users.serializers.ChangePasswordSerializer


class ResetPasswordView(ResetPasswordRequestToken):
    serializer_class = users.serializers.ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            response.data["status"] = "Ok"

        return response


class ResetPasswordConfirmView(ResetPasswordConfirm):
    serializer_class = users.serializers.ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            response.data["status"] = "Ok"

        return response
