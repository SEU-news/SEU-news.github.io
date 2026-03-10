"""
工具视图

包含：统一上传、搜索、预览
"""

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ContentSerializer
from api.permissions import IsEditorOrAdmin
from api.services.file_service import FileService
from api.services.content_service import ContentService
from api.services.pdf_service import PDFService
from api.core.exceptions import APIException


logger = logging.getLogger(__name__)


class UnifiedUploadAPIView(APIView):
    """
    统一上传 API
    支持：纯文本消息、URL 粘贴、图片上传（多图）
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            upload_type = request.data.get('upload_type')

            if upload_type == 'text':
                return self._handle_text_upload(request)
            elif upload_type == 'url':
                return self._handle_url_upload(request)
            elif upload_type == 'image':
                return self._handle_image_upload(request)
            else:
                return Response(
                    {'success': False, 'message': '无效的上传类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )

    def _handle_text_upload(self, request):
        """处理纯文本消息上传"""
        try:
            # 使用服务层创建内容
            content = ContentService.create_content(request.user, request.data)

            content_serializer = ContentSerializer(content, context={'request': request})
            return Response(content_serializer.data, status=status.HTTP_201_CREATED)
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )

    def _handle_url_upload(self, request):
        """处理 URL 粘贴"""
        try:
            url = request.data.get('url')
            if not url:
                return Response(
                    {'success': False, 'message': 'URL不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 使用服务层创建内容
            content = FileService.create_content_from_url(url, request.user)

            content_serializer = ContentSerializer(content, context={'request': request})
            return Response(content_serializer.data, status=status.HTTP_201_CREATED)
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )

    def _handle_image_upload(self, request):
        """处理图片上传（支持多图）"""
        try:
            images = request.FILES.getlist('images')
            if not images:
                return Response(
                    {'success': False, 'message': '未找到图片文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 使用服务层上传图片
            result = FileService.upload_multiple_images(images, request.user)

            return Response({
                'success': True,
                'image_urls': result
            }, status=status.HTTP_201_CREATED)
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )


@method_decorator(csrf_exempt, name='dispatch')
class SearchAPIView(APIView):
    """
    搜索 API

    POST /api/search/
    请求体: {"q": "搜索关键词"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            query = request.data.get('q', '').strip()

            if not query:
                return Response({
                    'success': True,
                    'count': 0,
                    'results': []
                })

            # 使用服务层搜索内容
            results = ContentService.search_content(query, request.user)

            serializer = ContentSerializer(results, many=True, context={'request': request})
            return Response({
                'success': True,
                'count': len(results),
                'results': serializer.data
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )


@method_decorator(csrf_exempt, name='dispatch')
class PreviewAPIView(APIView):
    """
    预览编辑

    POST /api/preview/
    请求体: {"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        try:
            content_ids = request.data.get('content_ids', [])

            # 使用服务层生成预览
            result = PDFService.preview_edit(content_ids)

            return Response({
                'success': True,
                'preview': result['preview']
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
