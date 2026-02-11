"""
内容管理视图

包含：内容列表/创建、详情/更新/删除、描述、审核、撤回、取消、状态更新
"""

import logging

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
    ContentDescribeSerializer,
    ContentModifySerializer,
)
from api.permissions import IsEditorOrAdmin, IsOwnerOrAdmin, IsCreatorOrAdmin, IsAdmin


logger = logging.getLogger(__name__)


class ContentListAPIView(generics.ListCreateAPIView):
    """
    内容列表 API
    GET: 获取内容列表（分页）
    POST: 创建新内容（需要 Editor 权限）
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContentCreateSerializer
        return ContentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsEditorOrAdmin()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # 自定义 create 方法，确保返回正确的响应
        logger.info(f'POST data: {request.data}')
        logger.info(f'POST data type: {type(request.data)}')

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f'Serializer validation errors: {serializer.errors}')
            logger.error(f'Serializer validated_data: {serializer.validated_data}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f'Serializer validated data: {serializer.validated_data}')

        # 保存实例
        self.perform_create(serializer)

        # 检查 instance
        if not hasattr(serializer, 'instance') or serializer.instance is None:
            logger.error('Serializer.instance is None after perform_create!')
            return Response({'error': 'Failed to create content'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        content = serializer.instance
        logger.info(f'Created content: id={content.id}, title={content.title}, type={content.type}')

        headers = self.get_success_headers(serializer.data)
        # 返回创建的数据（使用 ContentSerializer 序列化）
        response_serializer = ContentSerializer(content, context={'request': request})

        logger.info(f'Response serializer data: {response_serializer.data}')

        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        # /manage/list 页面只显示白名单中的状态
        ALLOWED_STATUSES = ['draft', 'pending', 'reviewed', 'rejected', 'published']
        queryset = Content.objects.filter(status__in=ALLOWED_STATUSES).order_by('-updated_at')

        # 搜索
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(title__icontains=query)

        # 排序
        sort_field = self.request.query_params.get('sort', 'updated_at')
        sort_order = self.request.query_params.get('order', 'desc')
        allowed_fields = ['id', 'created_at', 'updated_at', 'deadline', 'title']

        if sort_field in allowed_fields:
            order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field
            queryset = queryset.order_by(order_by)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        legal_sizes = [10, 20, 50, 100]

        if page_size not in legal_sizes:
            page_size = 10

        total = queryset.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 当前页数据
        results = queryset[offset:offset + page_size]

        serializer = ContentSerializer(results, many=True, context={'request': request})
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': serializer.data
        })


class ContentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    内容详情 API
    GET: 获取内容详情
    PUT/PATCH: 更新内容（需要 Editor 权限或为创建者）
    DELETE: 删除内容（需要为创建者）
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Content.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContentUpdateSerializer
        return ContentSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsCreatorOrAdmin()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContentSerializer(instance, context={'request': request})
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ContentDescribeAPIView(APIView):
    """
    内容描述/修改 API
    POST: 修改内容（需要 Editor 权限）
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response({'success': False, 'message': '内容不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 使用 ContentModifySerializer 验证数据
        serializer = ContentModifySerializer(content, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response({'success': False, 'message': '数据验证失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        logger.info(f"内容修改: {pk}, user={request.user.username}")
        return Response({'success': True, 'message': '修改成功'})


@method_decorator(csrf_exempt, name='dispatch')
class ContentReviewAPIView(APIView):
    """
    内容审核 API
    POST: 审核内容（通过/拒绝）（需要 Editor 或 Admin 权限）
    注意：不能审核自己创建或描述的内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 检查不能审核自己创建或描述的内容
        if request.user.id == content.creator_id or request.user.id == content.describer_id:
            return Response(
                {'success': False, 'message': '不可审核自己所写的内容！'},
                status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get('action')  # 'approve' or 'reject'
        comment = request.data.get('comment', '')

        if action not in ['approve', 'reject']:
            return Response(
                {'success': False, 'message': '无效的操作'},
                status=status.HTTP_400_BAD_REQUEST
            )

        content.reviewer_id = request.user.id

        if action == 'approve':
            content.status = 'reviewed'
        else:
            content.status = 'rejected'

        content.save()

        logger.info(f"内容审核: {pk}, action={action}, reviewer={request.user.username}")
        return Response({'success': True, 'message': '审核成功'})


@method_decorator(csrf_exempt, name='dispatch')
class ContentRecallAPIView(APIView):
    """
    内容撤回 API
    POST: 撤回内容（需要为创建者）
    """
    permission_classes = [IsAuthenticated, IsCreatorOrAdmin]
    queryset = Content.objects.all()

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 设置为草稿状态（撤回到草稿）
        content.status = 'draft'
        content.save()

        logger.info(f"内容撤回: {pk}, user={request.user.username}")
        return Response({'success': True, 'message': '撤回成功'})


@method_decorator(csrf_exempt, name='dispatch')
class ContentCancelAPIView(APIView):
    """
    取消内容
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(id=pk)
            content.status = 'cancelled'
            content.save()
            return Response({'success': True, 'message': '内容已取消'})
        except Content.DoesNotExist:
            return Response({'success': False, 'message': '内容不存在'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class ContentStatusUpdateAPIView(APIView):
    """
    内容状态更新 API
    POST: 修改内容状态（需要 Admin 权限）
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            content = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response(
                {'success': False, 'message': '内容不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        # 验证状态转换的有效性
        valid_transitions = {
            'draft': ['terminated', 'pending'],
            'pending': ['draft', 'reviewed', 'rejected', 'terminated'],
            'reviewed': ['draft', 'published', 'terminated'],
            'rejected': ['draft', 'terminated'],
            'published': ['terminated'],
            'terminated': ['draft'],
        }

        current_status = content.status

        if new_status not in valid_transitions.get(current_status, []):
            return Response(
                {'success': False, 'message': f'无法从 {current_status} 转换到 {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 清除相关字段（状态转换时）
        if new_status == 'draft':
            content.reviewer_id = None
        elif new_status in ['reviewed', 'rejected']:
            content.reviewer_id = request.user.id

        content.status = new_status
        content.save()

        logger.info(f"内容状态更新: {pk}, {current_status} -> {new_status}, user={request.user.username}")
        return Response({'success': True, 'message': '状态更新成功'})


class AdminContentListAPIView(generics.ListAPIView):
    """
    管理员内容列表 API
    GET: 获取所有内容列表（包括所有状态，如 terminated）
    /manage/admin/entries 专用
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        return ContentSerializer

    def get_queryset(self):
        # 管理员页面显示所有状态
        queryset = Content.objects.all().order_by('-updated_at')

        # 搜索
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(title__icontains=query)

        # 排序
        sort_field = self.request.query_params.get('sort', 'updated_at')
        sort_order = self.request.query_params.get('order', 'desc')
        allowed_fields = ['id', 'created_at', 'updated_at', 'deadline', 'title']

        if sort_field in allowed_fields:
            order_by = f"-{sort_field}" if sort_order == 'desc' else sort_field
            queryset = queryset.order_by(order_by)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        legal_sizes = [10, 20, 50, 100]

        if page_size not in legal_sizes:
            page_size = 10

        total = queryset.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # 当前页数据
        results = queryset[offset:offset + page_size]

        serializer = ContentSerializer(results, many=True, context={'request': request})
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'results': serializer.data
        })
