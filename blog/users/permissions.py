from rest_framework import permissions


class IsMe(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id
