from rest_framework import permissions


class IsMyComment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
