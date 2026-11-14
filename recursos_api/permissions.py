from rest_framework import permissions


class EsStaffOSoloLectura(permissions.BasePermission):
    """Lectura para usuarios autenticados; escritura solo para staff."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.method in permissions.SAFE_METHODS or request.user.is_staff
