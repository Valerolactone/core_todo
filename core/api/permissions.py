from rest_framework.permissions import BasePermission


class IsJWTAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user_info is not None


class IsJWTAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user_info is not None and request.user_info.get("role") == 'admin'
        )
