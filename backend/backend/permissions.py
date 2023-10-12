from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Everyone else can only read.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has the required permission.
        SAFE_METHODS include GET, HEAD, or OPTIONS.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
