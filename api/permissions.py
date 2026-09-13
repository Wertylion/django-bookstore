from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read access to everyone and write access only to admins."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    """Allow object access to owners; admins can read every object."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff and request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'owner_id', None) == getattr(request.user, 'id', None)
