from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.is_staff or
                request.user.groups.filter(name='Moderators').exists()
        )
