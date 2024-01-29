from rest_framework import permissions


class IsInGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=view.required_group).exists()


class IsOwnerObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and obj.user == request.user
        )
