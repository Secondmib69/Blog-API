from django.contrib import admin
from .models import Post, Comment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created', 'status', 'slug']
    list_editable = ['status']
    # readonly_fields = ['slug']

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'is_staff']
    list_editable = ['is_staff']
    list_display_links = ['username']
    fieldsets = (
                (None, {'fields': ('username', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'job_title', 'bio')}),
                ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),}),
                ('Important dates', {'fields': ('last_login', 'date_joined')})
                )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'email',
                'phone',
                'job_title',
                'bio',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
    )

    def get_readonly_fields(self, request, obj=None):

        readonly_fields = ['job_title', 'phone', 'username', 'password', 'first_name', 'last_name', 'email',
                'date_joined', 'last_login']
        if not obj:
            return []
        if request.user == obj:
            return []
        return readonly_fields
    
    def has_change_permission(self, request, obj=None):
        has_perm = super().has_change_permission(request, obj)

        if obj and obj.is_superuser and request.user != obj:
            return False

        return has_perm
    
    def has_delete_permission(self, request, obj=None):
        has_perm = super().has_delete_permission(request, obj)

        if obj and obj.is_superuser and request.user != obj:
            return False

        return has_perm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created', 'is_active']
    list_editable = ['is_active']