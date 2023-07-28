from django.conf import settings
from django_rest_passwordreset.views import ResetPasswordConfirm, ResetPasswordRequestToken
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import decorators, generics, mixins, permissions

import users.filters
import users.models
import users.serializers
from core.viewsets import ActionViewSet


@extend_schema_view(
    retrieve=extend_schema(
        description=(
            "Detailed user info. By default, sensitive fields (`email`) will have `null` value "
            "but authorized user will see his own email, e.g. when `is_me=true`"
            "\n\n"
            "See also [me](#/users/users_me_retrieve)"
        )
    ),
    list=extend_schema(description=("List and / or filter users")),
)
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


@extend_schema_view(
    retrieve=extend_schema(
        description=("Same as [user detail](#/users/users_retrieve), but returns full info on current authorized user")
    ),
    partial_update=extend_schema(
        description=(
            "Updates current authorized user" "\n\n" "See also [change_password](#/auth/auth_change_password_create)"
        )
    ),
)
class UserMeViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    ActionViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    queryset = users.models.User.objects.all()
    action_serializers = {
        "partial_update": users.serializers.UserUpdateSerializer,
        "retrieve": users.serializers.UserDetailSerializer,
    }
    http_method_names = ["patch", "get"]

    def get_object(self):
        return self.request.user


@extend_schema(
    description=(
        "Register new user\n\n"
        "- Password gets hashed in the process\n\n"
        "- Username as well as email should be unique\n\n"
        "- With `email=null` user won't be able to receive emails"
    )
)
class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = users.serializers.RegisterSerializer


@extend_schema(
    description=(
        "Update current authotized user's password\n\n"
        "To update other user info see [update me](#/users/users_me_partial_update)"
    )
)
class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = users.serializers.ChangePasswordSerializer


@extend_schema(
    description=(
        "Send reset password email\n\n"
        "- Always returns Ok status to prevent data leakage\n\n"
        "- To enable email sending please make sure that email credentials are set in the admin panel\n\n"
        f"- Reset link is active for {settings.DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME} hour(s)"
    )
)
class ResetPasswordView(ResetPasswordRequestToken):
    serializer_class = users.serializers.ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            response.data["status"] = "Ok"

        return response


@extend_schema(description=("Reset password using token from email"))
class ResetPasswordConfirmView(ResetPasswordConfirm):
    serializer_class = users.serializers.ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            response.data["status"] = "Ok"

        return response
