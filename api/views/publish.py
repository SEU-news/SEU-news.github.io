"""
发布相关视图

包含：批量发布内容、生成Typst文档、生成LaTeX文档、PDF生成
"""

import json
import logging
import os
from datetime import datetime

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_models.models import Content
from api.permissions import IsEditorOrAdmin
from api.utils.publish_utils import (
    sort_content_by_category,
    generate_typst_data,
    compile_typst_pdf
)


logger = logging.getLogger(__name__)


def get_publish_config():
    """
    获取发布配置

    如果配置未设置（如通过manage.py运行时），返回默认配置
    """
    config = getattr(settings, 'PUBLISH_CONFIG', None)
    if config is None:
        # 默认配置（用于manage.py运行时）
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config = {
            'pdf_output_dir': os.path.join(base_dir, 'static/pdfs'),
            'json_archive_dir': os.path.join(base_dir, 'archived'),
            'latest_json_path': os.path.join(base_dir, 'static/latest.json'),
            'latest_pdf_path': os.path.join(base_dir, 'static/latest.pdf'),
            'typst_template_path': os.path.join(base_dir, 'static/news_template.typ'),
            'fonts_dir': os.path.join(base_dir, 'fonts'),
            'typst_command': os.path.join(base_dir, 'typst.exe') if os.name == 'nt' else 'typst',
        }
    return config


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


class PublishDataAPIView(APIView):
    """
    生成Flask兼容的JSON数据

    GET /api/publish/data/<date>/
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        """生成指定日期的Typst数据（Flask格式）"""
        try:
            typst_data = generate_typst_data(date)
            return Response({
                'success': True,
                'data': typst_data
            })
        except Exception as e:
            logger.error(f"生成Typst数据失败: {e}")
            return Response(
                {'success': False, 'message': f'生成数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeneratePDFAPIView(APIView):
    """
    生成PDF文件

    POST /api/publish/pdf/
    请求体: {"date": "2026-02-11"}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        config = get_publish_config()
        date_str = request.data.get('date')

        if not date_str:
            return Response(
                {'success': False, 'message': '请提供日期参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 验证日期格式
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 生成Typst数据
            typst_data = generate_typst_data(date_str)

            # 确保目录存在
            os.makedirs(config['pdf_output_dir'], exist_ok=True)
            os.makedirs(config['json_archive_dir'], exist_ok=True)
            os.makedirs(os.path.dirname(config['latest_json_path']), exist_ok=True)
            os.makedirs(os.path.dirname(config['latest_pdf_path']), exist_ok=True)

            # 写入当前JSON文件
            json_str = json.dumps(typst_data, ensure_ascii=False, indent=2)
            with open(config['latest_json_path'], 'w', encoding='utf-8') as f:
                f.write(json_str)

            # 归档JSON文件
            archive_json_path = os.path.join(config['json_archive_dir'], f'{date_str}.json')
            with open(archive_json_path, 'w', encoding='utf-8') as f:
                f.write(json_str)

            # 编译PDF到latest.pdf
            pdf_result = compile_typst_pdf(
                json_path=config['latest_json_path'],
                output_path=config['latest_pdf_path'],
                fonts_dir=config['fonts_dir'],
                template_path=config['typst_template_path'],
                typst_cmd=config['typst_command']
            )

            if not pdf_result['success']:
                return Response(
                    {'success': False, 'message': pdf_result['message']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 归档PDF文件到pdfs目录
            import shutil
            archive_pdf_path = os.path.join(config['pdf_output_dir'], f'{date_str}.pdf')
            try:
                shutil.copy(config['latest_pdf_path'], archive_pdf_path)
            except Exception as e:
                logger.warning(f"归档PDF失败: {e}")

            # 返回PDF访问URL（直接使用latest.pdf，与Flask一致）
            pdf_url = "/static/latest.pdf"

            return Response({
                'success': True,
                'message': 'PDF生成成功',
                'pdf_url': pdf_url,
                'pdf_path': config['latest_pdf_path']
            })

        except Exception as e:
            logger.error(f"PDF生成失败: {e}")
            return Response(
                {'success': False, 'message': f'PDF生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryPublishedByDateAPIView(APIView):
    """
    按日期查询已发布内容

    支持两种查询方式：
    1. 路径参数: GET /api/publish/query/<date>/  - 查询单日
    2. 查询参数: GET /api/publish/query/?start_date=...&end_date=... - 查询日期范围
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date=None):
        # 支持单日期查询（通过URL路径）
        if date:
            try:
                publish_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # 查询该日期发布的内容
            contents = Content.objects.filter(
                status='published',
                publish_at__date=publish_date
            ).order_by('-publish_at')
        # 支持日期范围查询（通过查询参数）
        else:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            if not start_date_str or not end_date_str:
                return Response(
                    {'success': False, 'message': '请提供 start_date 和 end_date 参数'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 查询日期范围内发布的内容（包含开始和结束日期）
            contents = Content.objects.filter(
                status='published',
                publish_at__date__gte=start_date,
                publish_at__date__lte=end_date
            ).order_by('-publish_at')

        # 检查PDF是否存在（检查latest.pdf）
        config = get_publish_config()
        pdf_path = config['latest_pdf_path']
        pdf_exists = os.path.exists(pdf_path)
        # PDF URL始终指向latest.pdf（与Flask一致）
        pdf_url = "/static/latest.pdf" if pdf_exists else None

        return Response({
            'success': True,
            'start_date': request.query_params.get('start_date') or date,
            'end_date': request.query_params.get('end_date') or date,
            'published_contents': [
                {
                    'id': c.id,
                    'title': c.short_title or c.title,
                    'type': c.type,
                    'tag': c.tag,
                    'publish_at': c.publish_at.isoformat() if c.publish_at else None,
                }
                for c in contents
            ],
            'count': len(contents),
            'pdf_exists': pdf_exists,
            'pdf_url': pdf_url
        })


class UnpublishAPIView(APIView):
    """
    取消发布

    POST /api/publish/unpublish/
    请求体: {"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        content_ids = request.data.get('content_ids', [])

        if not content_ids:
            return Response(
                {'success': False, 'message': '请提供要取消发布的内容ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = 0
        failed_items = []

        for content_id in content_ids:
            try:
                content = Content.objects.get(id=content_id)
                # 只有已发布的内容才能取消发布
                if content.status == 'published':
                    content.status = 'reviewed'
                    content.publish_at = None
                    content.save()
                    updated_count += 1
                else:
                    failed_items.append({
                        'id': content_id,
                        'reason': f'状态为 {content.status}，不能取消发布'
                    })
            except Content.DoesNotExist:
                failed_items.append({'id': content_id, 'reason': '内容不存在'})

        return Response({
            'success': True,
            'updated': updated_count,
            'failed': failed_items
        })


class GeneratePDFFromSelectionAPIView(APIView):
    """
    根据选中的内容ID生成PDF

    POST /api/publish/pdf_from_selection/
    请求体: {"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def post(self, request):
        try:
            config = get_publish_config()
            content_ids = request.data.get('content_ids', [])

            if not content_ids:
                return Response(
                    {'success': False, 'message': '请提供内容ID列表'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 查询已发布的内容
            contents = Content.objects.filter(
                id__in=content_ids,
                status='published'
            )

            # 检查是否有有效内容
            if not contents.exists():
                return Response(
                    {'success': False, 'message': '没有找到有效的已发布内容'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"开始生成PDF，选中内容数: {len(contents)}")

            # 生成Typst数据（基于选中内容）
            typst_data = self._generate_typst_data_from_contents(contents)
            logger.info(f"Typst数据生成完成: {list(typst_data.keys())}")

            # 确保目录存在
            os.makedirs(os.path.dirname(config['latest_json_path']), exist_ok=True)
            os.makedirs(os.path.dirname(config['latest_pdf_path']), exist_ok=True)

            # 写入JSON
            json_str = json.dumps(typst_data, ensure_ascii=False, indent=2)
            with open(config['latest_json_path'], 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"JSON文件已写入: {config['latest_json_path']}")

            # 编译PDF
            pdf_result = compile_typst_pdf(
                json_path=config['latest_json_path'],
                output_path=config['latest_pdf_path'],
                fonts_dir=config['fonts_dir'],
                template_path=config['typst_template_path'],
                typst_cmd=config['typst_command']
            )

            logger.info(f"PDF编译结果: success={pdf_result['success']}, message={pdf_result.get('message')}")

            if not pdf_result['success']:
                return Response(
                    {'success': False, 'message': pdf_result['message']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 返回PDF URL和DDL数据
            return Response({
                'success': True,
                'message': 'PDF生成成功',
                'pdf_url': '/static/latest.pdf',
                'count': len(contents),
                'due_contents': typst_data.get('due', {})
            })
        except Exception as e:
            logger.error(f"PDF生成过程中发生异常: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'success': False, 'message': f'PDF生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_typst_data_from_contents(self, contents):
        """根据选中的内容生成Typst数据（Flask格式）"""
        from datetime import time

        # 分类普通内容
        categorized = sort_content_by_category(contents, is_deadline_content=False)

        # 计算结束日期：使用选中内容的最大发布时间
        # 如果没有内容，使用当前日期
        end_date = None
        for content in contents:
            if content.publish_at:
                if end_date is None or content.publish_at.date() > end_date:
                    end_date = content.publish_at.date()

        if end_date is None:
            end_date = datetime.now().date()

        start_of_day = datetime.combine(end_date, time.min)
        end_of_day = datetime.combine(end_date, time.max)

        # 获取截止日期内容（DDL在结束日期之后的）
        due_contents = Content.objects.filter(
            status='published',
            deadline__isnull=False,
            deadline__gt=end_of_day  # 使用 > 而不是 >=，确保DDL真正未到期
        ).order_by('deadline')

        categorized_due = sort_content_by_category(due_contents, is_deadline_content=True)

        # 返回Flask格式数据
        return {
            "data": {
                "date": end_date.strftime('%Y-%m-%d'),
                "no": 1,
                "first-v": 3,
                "lecture-v": 3,
                "other-v": 3,
                "college-v": 3,
                "club-v": 3,
                "college": categorized["college"],
                "club": categorized["club"],
                "lecture": categorized["lecture"],
                "other": categorized["other"]
            },
            "due": categorized_due
        }


class TypstAPIView(APIView):
    """
    生成Typst格式文档（使用Flask兼容格式）

    GET /api/typst/<date>/
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request, date):
        """返回Flask兼容的Typst JSON数据"""
        try:
            typst_data = generate_typst_data(date)
            return Response({
                'success': True,
                'date': date,
                'data': typst_data
            })
        except Exception as e:
            logger.error(f"生成Typst数据失败: {e}")
            return Response(
                {'success': False, 'message': f'生成数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryDDLByDateAPIView(APIView):
    """
    查询指定日期的DDL内容（未到期）

    GET /api/publish/ddl/?end_date=2026-02-11
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        from datetime import time

        end_date_str = request.query_params.get('end_date')
        if not end_date_str:
            return Response(
                {'success': False, 'message': '请提供 end_date 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'success': False, 'message': '日期格式无效'},
                status=status.HTTP_400_BAD_REQUEST
            )

        end_of_day = datetime.combine(end_date, time.max)
        logger.info(f"查询DDL: end_date={end_date_str}, end_of_day={end_of_day}")

        # 获取DDL内容（截止日期在结束日期之后）
        due_contents = Content.objects.filter(
            status='published',
            deadline__isnull=False,
            deadline__gt=end_of_day
        ).order_by('deadline')

        logger.info(f"找到DDL数量: {due_contents.count()}")

        # 对DDL内容进行分类
        categorized_due = sort_content_by_category(due_contents, is_deadline_content=True)

        # 扁平化分类结果以便前端展示
        all_due = []
        for category in ['other', 'lecture', 'college', 'club']:
            for item in categorized_due.get(category, []):
                # 格式化DDL数据用于前端展示
                all_due.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'due_time': item.get('due_time'),
                    'publish_date': item.get('publish_date'),
                    'category': category
                })

        return Response({
            'success': True,
            'due_contents': all_due,
            'count': len(all_due)
        })


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
            status='published',
            publish_at__date=publish_date
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
