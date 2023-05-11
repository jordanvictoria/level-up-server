from rest_framework import permissions

class UserCreateGameOrDelete(permissions.BasePermission):
    edit_methods = {"PUT", "DELETE"}
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.creator == request.user:
            return True
        if request.user.is_staff and request.meth not in self.edit_methods:
            return True
        return False