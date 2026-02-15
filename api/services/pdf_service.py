"""
PDF服务
处理PDF生成、Typst模板等功能
"""

from typing import Dict, Any, List, Union
import json
import os
from datetime import datetime

from django.conf import settings
from django_models.models import Content
from api.services.base_service import BaseService
from api.core.exceptions import ValidationError


class PDFService(BaseService):
    """PDF服务类"""

    @staticmethod
    def get_publish_config() -> Dict[str, Any]:
        """
        获取发布配置

        Returns:
            配置字典
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

    @staticmethod
    def generate_pdf_from_selection(date_str: str = None, content_ids: List[int] = None) -> Dict[str, Any]:
        """
        生成PDF（从日期或选中的内容）

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，可选
            content_ids: 内容ID列表，可选

        Returns:
            PDF生成结果

        Raises:
            ValidationError: 参数验证失败
        """
        from api.utils.publish_utils import compile_typst_pdf, generate_typst_data

        config = PDFService.get_publish_config()

        # 根据参数获取内容（优先使用 content_ids）
        if content_ids:
            # 从选中的内容生成
            contents = Content.objects.filter(
                id__in=content_ids,
                status='published'
            )

            if not contents.exists():
                raise ValidationError('没有找到有效的已发布内容')

            # 生成Typst数据（基于选中内容）
            typst_data = PDFService._generate_typst_data_from_contents(list(contents))
            count = len(contents)
            due_contents = typst_data.get('due', {})
            # 使用数据中的日期作为归档日期，如果提供了 date_str 则使用 date_str
            archive_date = date_str if date_str else typst_data.get('data', {}).get('date', datetime.now().strftime('%Y-%m-%d'))
        elif date_str:
            # 从日期生成（使用 publish_utils.generate_typst_data 返回 Flask 格式）
            typst_data = generate_typst_data(date_str)
            # 计算内容总数（所有分类的条目之和）
            data_categories = typst_data.get('data', {})
            count = sum(len(data_categories.get(cat, [])) for cat in ['college', 'club', 'lecture', 'other'])
            due_contents = typst_data.get('due', {})
            archive_date = date_str
        else:
            raise ValidationError('必须提供 date_str 或 content_ids 参数')

        # 确保目录存在
        os.makedirs(os.path.dirname(config['latest_json_path']), exist_ok=True)
        os.makedirs(os.path.dirname(config['latest_pdf_path']), exist_ok=True)
        os.makedirs(config['json_archive_dir'], exist_ok=True)
        os.makedirs(config['pdf_output_dir'], exist_ok=True)

        # 写入JSON（最新）
        json_str = json.dumps(typst_data, ensure_ascii=False, indent=2)
        with open(config['latest_json_path'], 'w', encoding='utf-8') as f:
            f.write(json_str)

        # 归档JSON数据
        archive_json_path = os.path.join(config['json_archive_dir'], f'{archive_date}.json')
        with open(archive_json_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

        # 编译PDF（最新）
        pdf_result = compile_typst_pdf(
            json_path=config['latest_json_path'],
            output_path=config['latest_pdf_path'],
            fonts_dir=config['fonts_dir'],
            template_path=config['typst_template_path'],
            typst_cmd=config['typst_command']
        )

        if not pdf_result['success']:
            return {
                'success': False,
                'message': pdf_result['message']
            }

        # 归档PDF
        archive_pdf_path = os.path.join(config['pdf_output_dir'], f'{archive_date}.pdf')
        import shutil
        shutil.copy2(config['latest_pdf_path'], archive_pdf_path)

        # 返回PDF URL
        return {
            'success': True,
            'pdf_url': '/static/latest.pdf',
            'pdf_path': config['latest_pdf_path'],
            'count': count,
            'due_contents': due_contents
        }

    @staticmethod
    def _generate_typst_data_from_contents(contents: List[Content]) -> Dict[str, Any]:
        """根据选中的内容生成Typst数据（Flask格式）"""
        from datetime import time
        from api.utils.publish_utils import sort_content_by_category

        # 分类普通内容
        categorized = sort_content_by_category(contents, is_deadline_content=False)

        # 计算结束日期：使用选中内容的最大发布时间
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
            deadline__gt=end_of_day
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

    @staticmethod
    def preview_edit(content_ids: List[int]) -> Dict[str, Any]:
        """
        预览编辑内容

        Args:
            content_ids: 内容ID列表

        Returns:
            预览数据

        Raises:
            ValidationError: 参数验证失败
        """
        if not content_ids:
            raise ValidationError('内容ID列表不能为空')

        # 获取内容对象
        contents = Content.objects.filter(id__in=content_ids)

        # 生成预览HTML
        html = '<div class="preview-container">'

        for content in contents:
            html += f'<h3>{content.title}</h3>'
            html += f'<p>{content.content}</p>'
            if content.link:
                html += f'<p><a href="{content.link}" target="_blank">来源链接</a></p>'
            html += '<hr>'

        html += '</div>'

        return {
            'preview': html
        }
