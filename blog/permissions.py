from rest_framework.permissions import BasePermission, SAFE_METHODS
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