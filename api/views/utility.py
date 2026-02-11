"""
工具视图

包含：统一上传、搜索、预览
"""

import logging
import os
import uuid
import json

from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import Content
from api.serializers import (
    ContentSerializer,
    ContentCreateSerializer,
)
from api.permissions import IsEditorOrAdmin


logger = logging.getLogger(__name__)


class UnifiedUploadAPIView(APIView):
    """
    统一上传 API
    支持：纯文本消息、URL 粘贴、图片上传（多图）
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
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

    def _handle_text_upload(self, request):
        """处理纯文本消息上传"""
        # 使用 ContentCreateSerializer 验证数据
        serializer = ContentCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        content = serializer.save()
        content_serializer = ContentSerializer(content, context={'request': request})
        return Response(content_serializer.data, status=status.HTTP_201_CREATED)

    def _handle_url_upload(self, request):
        """处理 URL 粘贴"""
        url = request.data.get('url')
        if not url:
            return Response(
                {'success': False, 'message': 'URL不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        content = Content.objects.create(
            creator_id=request.user.id,
            describer_id=request.user.id,
            title=url,
            link=url,
            content='',
            status='draft',
            type='其他'
        )

        content_serializer = ContentSerializer(content, context={'request': request})
        return Response(content_serializer.data, status=status.HTTP_201_CREATED)

    def _handle_image_upload(self, request):
        """处理图片上传（支持多图）"""
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'success': False, 'message': '未找到图片文件'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 保存所有图片
        image_paths = []
        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.name}"
            filepath = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # 保存相对路径
            image_paths.append(f"uploads/{filename}")

        # 创建 Content 对象
        content = Content.objects.create(
            creator_id=request.user.id,
            describer_id=request.user.id,
            title=f'图片上传_{len(images)}张',
            short_title=f'图片_{len(images)}张',
            link='',
            content=f'上传了 {len(images)} 张图片',
            status='draft',
            type='其他',
            image_list=json.dumps(image_paths)
        )

        content_serializer = ContentSerializer(content, context={'request': request})
        return Response(content_serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class SearchAPIView(APIView):
    """
    搜索 API
    POST: 搜索内容
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('q', '').strip()

        if not query:
            return Response({
                'success': True,
                'count': 0,
                'results': []
            })

        # 搜索标题和内容
        results = Content.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-updated_at')

        serializer = ContentSerializer(results, many=True, context={'request': request})
        return Response({
            'success': True,
            'count': results.count(),
            'results': serializer.data
        })


@method_decorator(csrf_exempt, name='dispatch')
class PreviewAPIView(APIView):
    """
    预览编辑
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        entries = request.data.get('entries', [])
        # 生成预览HTML/Markdown
        preview_html = self._generate_preview(entries)
        return Response({'success': True, 'preview': preview_html})

    def _generate_preview(self, entries):
        """生成预览HTML"""
        html = '<div class="preview-container">'

        for entry_id in entries:
            try:
                content = Content.objects.get(id=entry_id)
                html += f'<h3>{content.title}</h3>'
                html += f'<p>{content.content}</p>'
                if content.link:
                    html += f'<p><a href="{content.link}" target="_blank">来源链接</a></p>'
                html += '<hr>'
            except Content.DoesNotExist:
                pass

        html += '</div>'
        return html
