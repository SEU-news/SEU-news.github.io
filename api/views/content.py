"""
内容管理视图

包含：内容列表/创建、详情/更新/删除、描述、审核、撤回、取消
"""

import logging

import logging
from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import Content
from api.serializers import (
    ContentSerializer,
    ContentCreateSerializer,
    ContentUpdateSerializer,
)
from api.permissions import IsEditorOrAdmin, IsOwnerOrAdmin, IsCreatorOrAdmin, IsAdmin
from api.services import ContentService
from api.services.base_service import BaseService
from api.core.exceptions import APIException
from api.config.constants import ALLOWED_CONTENT_STATUSES


logger = logging.getLogger(__name__)


class ContentListAPIView(generics.ListAPIView):
    """
    内容列表 API
    GET: 获取内容列表（分页）
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return ContentSerializer

    def get_queryset(self):
        """
        获取查询集（根据用户权限动态控制）

        - 管理员：可以看到所有状态（包括 terminated）
        - 普通用户：只能看到活跃状态（排除 terminated）
        """
        # 管理员可以看到所有状态
        if self.request.user.has_admin_perm:
            return Content.objects.all().order_by('-updated_at')

        # 普通用户只能看到活跃状态（排除 terminated）
        return Content.objects.filter(status__in=ALLOWED_CONTENT_STATUSES).order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        """使用服务层分页"""
        queryset = self.filter_queryset(self.get_queryset())

        # 状态过滤（支持多值）
        status_param = request.query_params.get('status')
        if status_param:
            # 支持逗号分隔的多值: ?status=draft,pending
            status_values = [s.strip() for s in status_param.split(',')]
            queryset = queryset.filter(status__in=status_values)

        # 类型过滤（支持多值）
        type_param = request.query_params.get('type')
        if type_param:
            # 支持逗号分隔的多值: ?type=教务,竞赛
            type_values = [t.strip() for t in type_param.split(',')]
            queryset = queryset.filter(type__in=type_values)

        # 搜索
        query = request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(title__icontains=query)

        # ==================== 发布相关查询参数 ====================

        # 发布日期范围过滤
        publish_start_date = request.query_params.get('publish_start_date')
        publish_end_date = request.query_params.get('publish_end_date')
        if publish_start_date and publish_end_date:
            try:
                start = datetime.strptime(publish_start_date, '%Y-%m-%d')
                end = datetime.strptime(publish_end_date, '%Y-%m-%d')
                start_of_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = end.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(
                    publish_at__gte=start_of_day,
                    publish_at__lte=end_of_day
                )
            except ValueError:
                logger.warning(f"无效的发布日期格式: start={publish_start_date}, end={publish_end_date}")

        # 截止日期过滤（DDL 查询）
        deadline_end_date = request.query_params.get('deadline_end_date')
        if deadline_end_date:
            try:
                end_of_day = datetime.strptime(deadline_end_date, '%Y-%m-%d')
                end_of_day = end_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(deadline__gt=end_of_day)
            except ValueError:
                logger.warning(f"无效的截止日期格式: {deadline_end_date}")

        # 只返回已发布内容
        only_published = request.query_params.get('only_published', 'false').lower() == 'true'
        if only_published:
            queryset = queryset.filter(status='published')

        # 排序
        sort_field = request.query_params.get('sort', 'updated_at')
        sort_order = request.query_params.get('order', 'desc')
        allowed_fields = ['id', 'created_at', 'updated_at', 'deadline', 'title', 'publish_at']

        if sort_field in allowed_fields:
            order_prefix = '-' if sort_order == 'desc' else ''
            queryset = queryset.order_by(f'{order_prefix}{sort_field}')

        # 使用服务层分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        legal_sizes = [10, 20, 50, 100, 1000]

        if page_size not in legal_sizes:
            page_size = 10

        result = BaseService.paginate(queryset, page, page_size)

        # 序列化结果
        serializer = ContentSerializer(result['results'], many=True, context={'request': request})
        result['results'] = serializer.data

        return Response(result)


@method_decorator(csrf_exempt, name='dispatch')
class ContentCreateAPIView(APIView):
    """
    内容创建 API
    POST: 创建新内容（需要 Editor 权限）
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        """使用服务层创建内容"""
        try:
            content = ContentService.create_content(request.user, request.data)
            serializer = ContentSerializer(content, context={'request': request})
            logger.info(f"创建内容成功: id={content.id}, title={content.title}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except APIException as e:
            logger.error(f"创建内容失败: {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentDetailAPIView(generics.RetrieveAPIView):
    """
    内容详情 API
    GET: 获取内容详情（所有登录用户）
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Content.objects.all()

    def get_serializer_class(self):
        return ContentSerializer

    def retrieve(self, request, *args, **kwargs):
        """使用服务层获取内容详情"""
        try:
            instance = self.get_object()
            serializer = ContentSerializer(instance, context={'request': request})
            return Response(serializer.data)
        except APIException as e:
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentModifyAPIView(APIView):
    """
    内容更新 API
    PATCH: 更新内容（创建者或管理员）
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def patch(self, request, pk):
        """更新内容"""
        try:
            content = BaseService.get_object_or_404(Content, pk, '内容不存在')
            updated_instance = ContentService.update_content(content, request.data, request.user)
            serializer = ContentSerializer(updated_instance, context={'request': request})
            return Response(serializer.data)
        except APIException as e:
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentSubmitAPIView(APIView):
    """
    内容提交审核 API
    POST: 提交内容审核（需要 Editor 权限）

    纯状态转换操作：draft → pending
    - 不修改内容字段
    - 不修改 describer_id（提交者 ≠ 描述者）
    - 只改变 status
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        """使用服务层提交审核"""
        try:
            ContentService.submit_content(pk, request.user)
            logger.info(f"内容提交审核: {pk}, user={request.user.username}")
            return Response({
                'success': True,
                'message': '提交审核成功'
            })
        except APIException as e:
            logger.error(f"内容提交审核失败: {pk} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentReviewAPIView(APIView):
    """
    内容审核 API
    POST: 审核内容（通过/拒绝）（需要 Editor 权限）
    注意：不能审核自己创建的内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        """使用服务层审核内容"""
        try:
            # 转换 action 参数
            action = request.data.get('action')
            approved = (action == 'approve')
            comment = request.data.get('comment', '')

            content = ContentService.review_content(pk, request.user, approved, comment)

            logger.info(f"内容审核: {pk}, approved={approved}, reviewer={request.user.username}")
            return Response({
                'success': True,
                'message': '审核成功'
            })
        except APIException as e:
            logger.error(f"内容审核失败: {pk} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentRecallAPIView(APIView):
    """
    内容撤回 API
    POST: 撤回内容（需要为创建者或管理员）
    """
    permission_classes = [IsAuthenticated, IsCreatorOrAdmin]

    def post(self, request, pk):
        """使用服务层撤回内容"""
        try:
            content = ContentService.recall_content(pk, request.user)
            serializer = ContentSerializer(content, context={'request': request})
            logger.info(f"内容撤回: {pk}, user={request.user.username}")
            return Response({
                'success': True,
                'message': '撤回成功',
                'data': serializer.data
            })
        except APIException as e:
            logger.error(f"内容撤回失败: {pk} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentCancelAPIView(APIView):
    """
    取消内容 API
    POST: 取消内容（需要为创建者或管理员）
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        """使用服务层取消内容"""
        try:
            ContentService.cancel_content(pk, request.user)
            logger.info(f"内容取消: {pk}, user={request.user.username}")
            return Response({
                'success': True,
                'message': '内容已取消'
            })
        except APIException as e:
            logger.error(f"内容取消失败: {pk} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)


@method_decorator(csrf_exempt, name='dispatch')
class ContentAdminStatusAPIView(APIView):
    """
    管理员强制修改状态 API
    POST: 强制修改内容状态为任意有效值

    权限：管理员（role >= 2）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        """
        请求参数：
        - status (必需): 新状态值 (draft/pending/reviewed/rejected/published/terminated)
        - reason (可选): 状态变更原因（用于审计）
        """
        try:
            new_status = request.data.get('status')
            reason = request.data.get('reason', '')

            # 验证必需参数
            if not new_status:
                raise ValidationError('缺少必需参数: status')

            content = ContentService.admin_update_status(
                pk, request.user, new_status, reason
            )
            serializer = ContentSerializer(content, context={'request': request})
            return Response({
                'success': True,
                'message': '状态已强制更新',
                'data': serializer.data
            })
        except APIException as e:
            logger.error(f"管理员状态更新失败: {pk} - {e.message}")
            return Response({
                'success': False,
                'message': e.message
            }, status=e.status)
