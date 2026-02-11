"""
管理员视图

包含：用户列表、用户角色编辑、用户编辑、添加截止日期、管理面板数据
"""

import logging
import hashlib
from datetime import datetime

from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import User_info, Content
from api.serializers import UserSerializer
from api.permissions import IsAdmin


logger = logging.getLogger(__name__)


class UserAdminListAPIView(APIView):
    """
    用户列表 API
    GET: 获取用户列表（支持分页、排序、搜索、权限筛选）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        # 获取查询参数
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        sort_field = request.query_params.get('sort', 'created_at')
        sort_order = request.query_params.get('order', 'desc')
        query = request.query_params.get('q', '')
        role_filter = request.query_params.get('role', '')

        # 验证分页大小
        legal_sizes = [10, 20, 50, 100]
        if page_size not in legal_sizes:
            page_size = 10

        # 验证排序字段
        allowed_fields = ['id', 'username', 'realname', 'student_id', 'role', 'created_at']
        if sort_field not in allowed_fields:
            sort_field = 'created_at'

        # 构建查询集
        queryset = User_info.objects.all()

        # 搜索（用户名或学号）
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(student_id__icontains=query)
            )

        # 权限筛选
        if role_filter and role_filter.isdigit():
            queryset = queryset.filter(role=int(role_filter))

        # 排序
        order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field
        queryset = queryset.order_by(order_by)

        # 分页
        total = queryset.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 当前页数据
        results = queryset[offset:offset + page_size]

        # 序列化
        serializer = UserSerializer(results, many=True, context={'request': request})

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': serializer.data
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserRoleEditAPIView(APIView):
    """
    编辑用户角色
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        try:
            user = User_info.objects.get(id=user_id)
        except User_info.DoesNotExist:
            return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # 'add' or 'remove'
        permission = request.data.get('permission')  # 'editor' or 'admin'

        if permission == 'editor':
            perm_bit = User_info.PERMISSION_EDITOR
        elif permission == 'admin':
            perm_bit = User_info.PERMISSION_ADMIN
        else:
            return Response({'success': False, 'message': '无效的权限类型'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'add':
            user.role |= perm_bit
        elif action == 'remove':
            user.role &= ~perm_bit
        else:
            return Response({'success': False, 'message': '无效的操作'}, status=status.HTTP_400_BAD_REQUEST)

        user.save()
        return Response({'success': True, 'role': user.role, 'message': '角色更新成功'})


@method_decorator(csrf_exempt, name='dispatch')
class UserEditAPIView(APIView):
    """
    编辑用户信息
    支持字段：realname, student_id, password
    注意：password 字段需要管理员权限（或用户修改自己的密码）
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = User_info.objects.get(id=user_id)

            # 权限检查：只能编辑自己或管理员可以编辑任何人
            if user_id != request.user.id and not request.user.has_admin_perm:
                return Response({'success': False, 'message': '权限不足'}, status=status.HTTP_403_FORBIDDEN)

            # 更新字段
            if 'realname' in request.data:
                user.realname = request.data['realname']
            if 'student_id' in request.data:
                user.student_id = request.data['student_id']

            # 密码字段需要特殊处理
            if 'password' in request.data:
                password = request.data['password']

                # 权限检查：修改密码需要管理员权限或修改自己的密码
                if user_id != request.user.id and not request.user.has_admin_perm:
                    return Response({'success': False, 'message': '无权修改他人密码'}, status=status.HTTP_403_FORBIDDEN)

                # 密码验证
                if len(password) < 6:
                    return Response({'success': False, 'message': {'password': ['密码长度至少6位']}}, status=status.HTTP_400_BAD_REQUEST)

                user.password_MD5 = hashlib.md5(password.encode('utf-8')).hexdigest()
                logger.info(f"用户 {request.user.username} 修改了用户 {user.username} 的密码")

            user.save()
            serializer = UserSerializer(user)
            return Response({'success': True, 'user': serializer.data, 'message': '用户信息更新成功'})

        except User_info.DoesNotExist:
            return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class AddDeadlineAPIView(APIView):
    """
    添加截止日期 API（占位）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        content_id = request.data.get('content_id')
        deadline = request.data.get('deadline')

        if not content_id or not deadline:
            return Response({'success': False, 'message': 'content_id 和 deadline 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            deadline_dt = datetime.fromisoformat(deadline)

            content = Content.objects.get(id=content_id)
            content.deadline = deadline_dt
            content.save()

            logger.info(f"用户 {request.user.username} 为内容 {content_id} 设置截止日期: {deadline}")

            return Response({'success': True, 'message': '截止日期设置成功'})
        except Content.DoesNotExist:
            return Response({'success': False, 'message': '内容不存在'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'success': False, 'message': '日期格式无效'}, status=status.HTTP_400_BAD_REQUEST)


class AdminDashboardAPIView(APIView):
    """
    管理面板数据
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from django.utils import timezone

        # 统计数据
        total_users = User_info.objects.count()
        total_contents = Content.objects.count()
        pending_reviews = Content.objects.filter(status='pending').count()
        published_today = Content.objects.filter(
            status='published',
            publish_at__date=timezone.now().date()
        ).count()

        # 状态分布统计（使用 aggregation 高效计算）
        status_stats = Content.objects.values('status').annotate(count=Count('id'))
        status_counts = {stat['status']: stat['count'] for stat in status_stats}

        # 确保所有状态都有值（为空则返回 0）
        all_statuses = ['draft', 'pending', 'reviewed', 'rejected', 'published', 'terminated']
        for s in all_statuses:
            status_counts.setdefault(s, 0)

        return Response({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_contents': total_contents,
                'pending_reviews': pending_reviews,
                'published_today': published_today,
                'status_counts': status_counts
            }
        })
