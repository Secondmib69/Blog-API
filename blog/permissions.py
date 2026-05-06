from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from .models import Post



class IsPostAuthorOrStaffDeleteOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (request.user == obj.author) or
            ((request.user.is_superuser or request.user.is_staff) and request.method == 'DELETE') or
            (request.method in SAFE_METHODS)
        )
    

class IsStaffOrCommentUserDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            (request.user == obj.user and request.method in (*SAFE_METHODS, 'DELETE')) or
            (request.user.is_superuser or request.user.is_staff)
        )
    

class UserRolePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method


        return bool(
            (user.is_superuser and obj.is_superuser and method in SAFE_METHODS) or
            (user.is_superuser and not obj.is_superuser) or
            (user.is_staff and (obj.is_superuser or obj.is_staff) and method in SAFE_METHODS) or
            (user.is_staff and not (obj.is_superuser or obj.is_staff)) or
            (method in SAFE_METHODS or user == obj)
        )
    
    # def has_permission(self, request, view):
    #     if view.action == 'create':
    #         return request.user.is_superuser
    #     return True