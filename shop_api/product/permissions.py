
from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    message = 'У вас нет прав модератора для этого действия.'

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_staff:
            return False

        if request.method == 'POST':
            return False

        return request.method in ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'DELETE']
