"""
发布相关视图

包含：批量发布内容、生成Typst文档、生成LaTeX文档
"""

import logging
from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import Content
from api.permissions import IsEditorOrAdmin


logger = logging.getLogger(__name__)


class PublishAPIView(APIView):
    """
    批量发布内容
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        from django.utils import timezone

        # 兼容前端发送的 entries 字段名
        content_ids = request.data.get('content_ids') or request.data.get('entries', [])
        if not content_ids:
            return Response(
                {'success': False, 'message': '请提供要发布的内容ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        failed_items = []

        for content_id in content_ids:
            try:
                content = Content.objects.get(id=content_id)
                # 只有已审核的内容才能发布
                if content.status == 'reviewed':
                    content.status = 'published'
                    content.publish_at = timezone.now()
                    content.save()
                    updated_count += 1
                else:
                    failed_items.append({
                        'id': content_id,
                        'reason': f'状态为 {content.status}，不能发布'
                    })
            except Content.DoesNotExist:
                failed_items.append({'id': content_id, 'reason': '内容不存在'})

        return Response({
            'success': True,
            'updated': updated_count,
            'failed': failed_items
        })


class TypstAPIView(APIView):
    """
    生成Typst格式文档
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        from django.utils import timezone

        try:
            publish_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查询该日期发布的内容
        contents = Content.objects.filter(
            publish_at__date=publish_date,
            status='published'
        ).order_by('-publish_at')

        typst_content = self._generate_typst(contents)

        return Response({
            'success': True,
            'date': date,
            'count': len(contents),
            'typst': typst_content
        })

    def _generate_typst(self, contents):
        """生成 Typst 格式文档"""
        lines = [
            '# 新闻简报',
            f'发布日期: {timezone.now().strftime("%Y年%m月%d日")}',
            ''
        ]

        for content in contents:
            lines.extend([
                f'## {content.title}',
                f'{content.content}',
                f'来源: {content.link}',
                ''
            ])

        return '\n'.join(lines)


class LatexAPIView(APIView):
    """
    生成LaTeX格式文档
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        from django.utils import timezone

        try:
            publish_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查询该日期发布的内容
        contents = Content.objects.filter(
            publish_at__date=publish_date,
            status='published'
        ).order_by('-publish_at')

        latex_content = self._generate_latex(contents)

        return Response({
            'success': True,
            'date': date,
            'count': len(contents),
            'latex': latex_content
        })

    def _generate_latex(self, contents):
        """生成 LaTeX 格式文档"""
        from django.utils import timezone

        lines = [
            '\\documentclass{article}',
            '\\usepackage{ctex}',
            '\\begin{document}',
            '\\title{新闻简报}',
            f'\\author{{发布日期: {timezone.now().strftime("%Y年%m月%d日")}}}',
            '\\maketitle',
            ''
        ]

        for content in contents:
            lines.extend([
                f'\\section*{{{content.title}}}',
                f'{content.content}',
                f'\\textbf{{来源: {content.link}}}',
                ''
            ])

        lines.append('\\end{document}')
        return '\n'.join(lines)
