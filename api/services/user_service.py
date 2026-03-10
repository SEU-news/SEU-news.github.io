"""
用户服务
处理用户管理、权限检查、角色管理等功能
"""

from typing import Dict, Any
from django.db.models import Q
from api.django_models import User_info, Content
from api.core.exceptions import ValidationError, PermissionDeniedError
from api.services.base_service import BaseService


class UserService(BaseService):
    """用户服务类"""

    @staticmethod
    def has_editor_permission(user: User_info) -> bool:
        """
        检查用户是否有编辑权限

        Args:
            user: 用户对象

        Returns:
            是否有编辑权限
        """
        return user.has_editor_perm

    @staticmethod
    def has_admin_permission(user: User_info) -> bool:
        """
        检查用户是否有管理员权限

        Args:
            user: 用户对象

        Returns:
            是否有管理员权限
        """
        return user.has_admin_perm

    @staticmethod
    def get_users_list(
        query: str = '',
        role_filter: int = None,
        sort_field: str = 'created_at',
        sort_order: str = 'desc',
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取用户列表

        Args:
            query: 搜索关键词（用户名或真实姓名）
            role_filter: 角色过滤（0=用户, 1=编辑, 2=管理员, 3=超管）
            sort_field: 排序字段
            sort_order: 排序方向（asc/desc）
            page: 页码
            page_size: 每页条数

        Returns:
            分页的用户列表
        """
        # 构建查询
        users = User_info.objects.all()

        # 搜索过滤
        if query:
            users = users.filter(
                Q(username__icontains=query) | Q(realname__icontains=query)
            )

        # 角色过滤
        if role_filter is not None:
            users = users.filter(role=role_filter)

        # 排序
        order_prefix = '' if sort_order == 'asc' else '-'
        allowed_sort_fields = ['id', 'username', 'realname', 'student_id', 'created_at', 'role']
        if sort_field in allowed_sort_fields:
            users = users.order_by(f'{order_prefix}{sort_field}')
        else:
            users = users.order_by('-created_at')

        # 分页
        result = UserService.paginate(users, page, page_size)

        return result

    @staticmethod
    def update_user_role(user: User_info, new_role: int, operator: User_info) -> User_info:
        """
        更新用户角色

        Args:
            user: 要更新的用户对象
            new_role: 新角色（0=用户, 1=编辑, 2=管理员, 3=超管）
            operator: 操作者用户对象

        Returns:
            更新后的用户对象

        Raises:
            ValidationError: 参数验证失败
            PermissionDeniedError: 无权限修改角色
        """
        # 权限检查：只有管理员可以修改角色
        if not operator.has_admin_perm:
            raise PermissionDeniedError('需要管理员权限才能修改用户角色')

        # 验证角色值
        if new_role not in [0, 1, 2, 3]:
            raise ValidationError('无效的角色值，必须是 0, 1, 2 或 3')

        # 不能修改自己的角色
        if user.id == operator.id:
            raise ValidationError('不能修改自己的角色')

        # 更新角色
        user.role = new_role
        user.save(update_fields=['role'])

        return user

    @staticmethod
    def update_user_info(user: User_info, data: Dict[str, Any], operator: User_info) -> User_info:
        """
        更新用户信息

        Args:
            user: 要更新的用户对象
            data: 更新数据
            operator: 操作者用户对象

        Returns:
            更新后的用户对象

        Raises:
            ValidationError: 参数验证失败
            PermissionDeniedError: 无权限修改
        """
        # 权限检查：用户可以修改自己的信息，管理员可以修改任何人
        can_modify = (user.id == operator.id) or operator.has_admin_perm
        if not can_modify:
            raise PermissionDeniedError('只有本人或管理员可以修改用户信息')

        # 允许更新的字段
        allowed_fields = ['realname', 'student_id', 'avatar']
        if operator.has_admin_perm:
            allowed_fields.extend(['username', 'role'])

        # 更新字段
        for field in allowed_fields:
            if field in data:
                # 特殊检查：用户名不能重复
                if field == 'username' and data[field] != user.username:
                    if User_info.objects.filter(username=data[field]).exists():
                        raise ValidationError('用户名已存在')

                setattr(user, field, data[field])

        user.save()

        return user

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """
        获取管理面板统计数据

        Returns:
            统计数据字典
        """
        from django.utils import timezone

        # 用户统计
        total_users = User_info.objects.count()

        # 内容统计
        total_contents = Content.objects.count()

        # 状态统计
        draft_contents = Content.objects.filter(status='draft').count()
        pending_contents = Content.objects.filter(status='pending').count()
        reviewed_contents = Content.objects.filter(status='reviewed').count()
        rejected_contents = Content.objects.filter(status='rejected').count()
        published_contents = Content.objects.filter(status='published').count()
        terminated_contents = Content.objects.filter(status='terminated').count()

        # 今日发布统计
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today = Content.objects.filter(
            status='published',
            publish_at__gte=today_start
        ).count()

        return {
            'total_users': total_users,
            'total_contents': total_contents,
            'pending_reviews': pending_contents,
            'published_today': published_today,
            'status_counts': {
                'draft': draft_contents,
                'pending': pending_contents,
                'reviewed': reviewed_contents,
                'rejected': rejected_contents,
                'published': published_contents,
                'terminated': terminated_contents
            }
        }
