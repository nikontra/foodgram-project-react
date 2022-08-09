from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Пермишен для автора или только чтение"""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and (request.user == obj.author)
        )
