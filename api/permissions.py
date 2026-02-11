"""
API 权限控制

定义自定义权限类用于 API 访问控制
"""

from rest_framework import permissions


class IsEditorOrAdmin(permissions.BasePermission):
    """
    检查用户是否有编辑或管理员权限
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_editor_permission()


class IsAdmin(permissions.BasePermission):
    """
    检查用户是否有管理员权限
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_admin_permission()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    检查用户是否是资源所有者或管理员
    用于 Content 对象操作
    """
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有对象
        if request.user.has_admin_permission():
            return True

        # 只有创建者可以访问自己的对象
        return obj.creator_id == request.user.id


class IsCreatorOrAdmin(permissions.BasePermission):
    """
    检查用户是否是内容创建者或管理员
    """
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问
        if request.user.has_admin_permission():
            return True

        # 只有创建者可以删除
        return obj.creator_id == request.user.id
