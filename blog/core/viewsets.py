from rest_framework import serializers
from rest_framework import permissions
from rest_framework.viewsets import GenericViewSet
from django.db import models
import typing as t


class ActionViewSet(GenericViewSet):
    action_serializers: dict[str, t.Type[serializers.Serializer]] = {}
    action_permissions: dict[str, t.Type[permissions.BasePermission]] = {}
    action_querysets: dict[str, models.QuerySet] = {}

    def get_serializer_class(self):
        ser = self.action_serializers.get(self.action, self.serializer_class)

        if ser is None and getattr(self, 'swagger_fake_view', False):
            msg = [
                f"Swagger generation failed at {self.__class__.__name__}",
                f"Action: {self.action}",
                f"HTTP method: {self.request.method}",
            ]
            raise ValueError("\n".join(msg))

        return ser

    def get_permissions(self):
        permission_classes = self.action_permissions.get(self.action, self.permission_classes)
        return [one() for one in permission_classes]

    def get_queryset(self):
        queryset = self.action_querysets.get(self.action, self.queryset)
        return queryset
