"""
发布服务
处理内容发布、Typst 生成、LaTeX 生成等业务逻辑
"""

from typing import Dict, Any, List, Union
from datetime import datetime
from django.db.models import Q
from django_models.models import User_info, Content
from api.core.exceptions import ValidationError, BusinessLogicError
from api.services.base_service import BaseService


class PublishService(BaseService):
    """发布服务类"""

    @staticmethod
    def publish_contents(user: User_info, content_ids: List[int]) -> Dict[str, Any]:
        """
        批量发布内容

        Args:
            user: 当前用户（用于权限检查）
            content_ids: 内容ID列表

        Returns:
            包含更新数量和失败项的字典

        Raises:
            ValidationError: 参数验证失败
        """
        if not content_ids:
            raise ValidationError('内容ID列表不能为空')

        updated_count = 0
        failed_items = []

        for content_id in content_ids:
            try:
                content = Content.objects.get(id=content_id)
                # 只有已审核的内容才能发布
                if content.status == 'reviewed':
                    content.status = 'published'
                    content.publish_at = datetime.now()
                    content.save()
                    updated_count += 1
                else:
                    failed_items.append({
                        'id': content_id,
                        'reason': f'状态为 {content.status}，不能发布'
                    })
            except Content.DoesNotExist:
                failed_items.append({'id': content_id, 'reason': '内容不存在'})

        return {
            'updated': updated_count,
            'failed': failed_items
        }

    @staticmethod
    def generate_typst_data(date_or_contents: Union[str, datetime, List[Content]]) -> Dict[str, Any]:
        """
        生成 Typst 数据

        Args:
            date_or_contents: 日期字符串 (YYYY-MM-DD) 或内容列表

        Returns:
            Typst 数据字典

        Raises:
            ValidationError: 参数验证失败
        """
        # 获取内容列表
        if isinstance(date_or_contents, str):
            # 从日期获取
            try:
                target_date = datetime.strptime(date_or_contents, '%Y-%m-%d')
            except ValueError:
                raise ValidationError('日期格式错误，应为 YYYY-MM-DD')

            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # 查询当天发布的内容
            contents = Content.objects.filter(
                status='published',
                publish_at__gte=start_of_day,
                publish_at__lte=end_of_day
            ).order_by('type', '-publish_at')

        elif isinstance(date_or_contents, datetime):
            # 从 datetime 获取
            target_date = date_or_contents
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            contents = Content.objects.filter(
                status='published',
                publish_at__gte=start_of_day,
                publish_at__lte=end_of_day
            ).order_by('type', '-publish_at')

        elif isinstance(date_or_contents, list):
            # 直接使用内容列表
            contents = date_or_contents

        else:
            raise ValidationError('无效的参数类型')

        # 按类型分类
        from api.config.constants import CONTENT_TYPES

        categorized = {type_: [] for type_ in CONTENT_TYPES}

        for content in contents:
            if content.type in categorized:
                categorized[content.type].append({
                    'title': content.title,
                    'short_title': content.short_title or content.title,
                    'link': content.link,
                    'content': content.content,
                    'deadline': content.deadline.strftime('%Y-%m-%d') if content.deadline else '',
                })

        # 生成 Typst 数据
        typst_data = {
            'date': date_or_contents if isinstance(date_or_contents, str) else datetime.now().strftime('%Y-%m-%d'),
            'categories': categorized,
            'ddl_items': [],  # 未到期的DDL
        }

        # 提取有DDL且未到期的内容
        for content in contents:
            if content.deadline and content.deadline > datetime.now():
                typst_data['ddl_items'].append({
                    'title': content.title,
                    'deadline': content.deadline.strftime('%Y-%m-%d'),
                    'type': content.type,
                })

        return typst_data

    @staticmethod
    def generate_latex_data(date_or_contents: Union[str, datetime, List[Content]]) -> Dict[str, Any]:
        """
        生成 LaTeX 数据

        Args:
            date_or_contents: 日期字符串 (YYYY-MM-DD) 或内容列表

        Returns:
            LaTeX 数据字典

        Raises:
            ValidationError: 参数验证失败
        """
        # LaTeX 数据格式与 Typst 类似
        return PublishService.generate_typst_data(date_or_contents)
