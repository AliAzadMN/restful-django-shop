from rest_framework import permissions


class IsInGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=view.required_group).exists()
    