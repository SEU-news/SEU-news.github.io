"""
管理员视图

包含：用户列表、用户角色编辑、用户编辑、管理面板数据
"""

import logging
from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import User_info, Content
from api.serializers import UserSerializer
from api.permissions import IsAdmin
from api.services.user_service import UserService
from api.services.content_service import ContentService
from api.core.exceptions import APIException

logger = logging.getLogger(__name__)


class UserAdminListAPIView(APIView):
    """
    用户列表 API
    GET: 获取用户列表（支持分页、排序、搜索、权限筛选）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        try:
            # 获取查询参数
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            sort_field = request.query_params.get('sort', 'created_at')
            sort_order = request.query_params.get('order', 'desc')
            query = request.query_params.get('q', '')
            role_filter_str = request.query_params.get('role', '')

            # 验证分页大小
            legal_sizes = [10, 20, 50, 100]
            if page_size not in legal_sizes:
                page_size = 10

            # 验证排序字段
            allowed_fields = ['id', 'username', 'realname', 'student_id', 'role', 'created_at']
            if sort_field not in allowed_fields:
                sort_field = 'created_at'

            # 处理 role_filter：空字符串转为 None
            role_filter = None
            if role_filter_str and role_filter_str.isdigit():
                role_filter = int(role_filter_str)

            # 使用服务层获取用户列表
            result = UserService.get_users_list(
                page=page,
                page_size=page_size,
                sort_field=sort_field,
                sort_order=sort_order,
                query=query,
                role_filter=role_filter
            )

            # 序列化结果
            serializer = UserSerializer(result['results'], many=True, context={'request': request})

            return Response({
                'count': result['count'],
                'page': page,
                'page_size': page_size,
                'total_pages': result['total_pages'],
                'results': serializer.data
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )


@method_decorator(csrf_exempt, name='dispatch')
class UserRoleEditAPIView(APIView):
    """
    编辑用户角色

    POST /api/admin/users/<user_id>/role/
    请求体: {"action": "add|remove", "permission": "editor|admin"}
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        try:
            from django_models.models import User_info
            from api.services.base_service import BaseService

            # 使用服务层获取用户
            user = BaseService.get_object_or_404(User_info, user_id, '用户不存在')

            action = request.data.get('action')  # 'add' or 'remove'
            permission = request.data.get('permission')  # 'editor' or 'admin'

            # 计算权限位
            if permission == 'editor':
                perm_bit = User_info.PERMISSION_EDITOR
            elif permission == 'admin':
                perm_bit = User_info.PERMISSION_ADMIN
            else:
                return Response(
                    {'success': False, 'message': '无效的权限类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 计算新角色值
            if action == 'add':
                new_role = user.role | perm_bit
            elif action == 'remove':
                new_role = user.role & ~perm_bit
            else:
                return Response(
                    {'success': False, 'message': '无效的操作'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 使用服务层更新角色
            updated_user = UserService.update_user_role(user, new_role, request.user)

            serializer = UserSerializer(updated_user)
            return Response({
                'success': True,
                'user': serializer.data,
                'message': '角色更新成功'
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )


@method_decorator(csrf_exempt, name='dispatch')
class UserEditAPIView(APIView):
    """
    编辑用户信息

    PATCH /api/admin/users/<user_id>/info/
    支持字段：realname, student_id, password
    注意：password 字段需要管理员权限（或用户修改自己的密码）
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            from django_models.models import User_info
            from api.services.base_service import BaseService
            import hashlib

            # 使用服务层获取用户
            user = BaseService.get_object_or_404(User_info, user_id, '用户不存在')

            # 权限检查：只能编辑自己或管理员可以编辑任何人
            if user_id != request.user.id and not request.user.has_admin_perm:
                return Response(
                    {'success': False, 'message': '权限不足'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 处理密码更新（特殊处理）
            if 'password' in request.data:
                password = request.data['password']

                # 权限检查：修改密码需要管理员权限或修改自己的密码
                if user_id != request.user.id and not request.user.has_admin_perm:
                    return Response(
                        {'success': False, 'message': '无权修改他人密码'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # 密码验证
                if len(password) < 6:
                    return Response(
                        {'success': False, 'message': {'password': ['密码长度至少6位']}},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user.password_MD5 = hashlib.md5(password.encode('utf-8')).hexdigest()
                logger.info(f"用户 {request.user.username} 修改了用户 {user.username} 的密码")

                # 从 data 中移除 password，避免 update_user_info 处理
                update_data = {k: v for k, v in request.data.items() if k != 'password'}
            else:
                update_data = request.data

            # 使用服务层更新其他字段
            updated_user = UserService.update_user_info(user, update_data, request.user)

            serializer = UserSerializer(updated_user)
            return Response({
                'success': True,
                'user': serializer.data,
                'message': '用户信息更新成功'
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )



class AdminDashboardAPIView(APIView):
    """
    管理面板数据

    GET /api/admin/dashboard/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            stats = UserService.get_dashboard_stats()

            return Response({
                'success': True,
                'stats': stats
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
