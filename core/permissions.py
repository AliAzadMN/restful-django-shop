from rest_framework import permissions
    

class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            not request.user.is_authenticated 
        )
    
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_superuser
        )
    