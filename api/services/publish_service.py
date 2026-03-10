"""
发布服务
处理内容发布、Typst 生成、LaTeX 生成等业务逻辑
"""

from typing import Dict, Any, List, Union
from datetime import datetime
from api.django_models import User_info, Content
from api.core.exceptions import ValidationError
from api.services.base_service import BaseService

from api.logging import get_logger

logger = get_logger(__name__)


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
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        logger.info(f"开始批量发布内容, {user_info}, content_ids={content_ids}, count={len(content_ids)}")

        if not content_ids:
            logger.warning(f"批量发布失败: 内容ID列表为空, {user_info}")
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
                    logger.debug(f"内容发布成功: content_id={content_id}, title={content.title}, {user_info}")
                else:
                    reason = f'状态为 {content.status}，不能发布'
                    failed_items.append({'id': content_id, 'reason': reason})
                    logger.debug(f"内容发布跳过: content_id={content_id}, {reason}, {user_info}")
            except Content.DoesNotExist:
                reason = '内容不存在'
                failed_items.append({'id': content_id, 'reason': reason})
                logger.debug(f"内容发布失败: content_id={content_id}, {reason}, {user_info}")

        # 记录完成日志
        logger.info(
            f"批量发布完成, {user_info}, total={len(content_ids)}, "
            f"updated={updated_count}, failed={len(failed_items)}"
        )

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
        # 记录入口日志
        if isinstance(date_or_contents, str):
            logger.info(f"开始生成Typst数据, date={date_or_contents}")
        elif isinstance(date_or_contents, datetime):
            logger.info(f"开始生成Typst数据, datetime={date_or_contents}")
        elif isinstance(date_or_contents, list):
            logger.info(f"开始生成Typst数据, from_content_list, count={len(date_or_contents)}")
        else:
            logger.warning(f"开始生成Typst数据, 参数类型={type(date_or_contents).__name__}")

        # 获取内容列表
        if isinstance(date_or_contents, str):
            # 从日期获取
            try:
                target_date = datetime.strptime(date_or_contents, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"Typst数据生成失败: 日期格式错误, date={date_or_contents}, error={str(e)}", exc_info=True)
                raise ValidationError('日期格式错误，应为 YYYY-MM-DD')

            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # 查询当天发布的内容
            contents = Content.objects.filter(
                status='published',
                publish_at__gte=start_of_day,
                publish_at__lte=end_of_day
            ).order_by('type', '-publish_at')

            logger.debug(f"查询到发布内容: date={date_or_contents}, count={contents.count()}")

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

            logger.debug(f"查询到发布内容: datetime={date_or_contents}, count={contents.count()}")

        elif isinstance(date_or_contents, list):
            # 直接使用内容列表
            contents = date_or_contents
            logger.debug(f"使用传入内容列表: count={len(contents)}")

        else:
            logger.error(f"Typst数据生成失败: 无效参数类型, type={type(date_or_contents).__name__}")
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

        # 记录完成日志
        items_count = sum(len(v) for v in categorized.values())
        logger.info(
            f"Typst数据生成成功, categories={len(categorized)}, "
            f"items={items_count}, ddl_items={len(typst_data['ddl_items'])}"
        )

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
        # 记录入口日志
        if isinstance(date_or_contents, str):
            logger.info(f"开始生成LaTeX数据, date={date_or_contents}")
        elif isinstance(date_or_contents, datetime):
            logger.info(f"开始生成LaTeX数据, datetime={date_or_contents}")
        elif isinstance(date_or_contents, list):
            logger.info(f"开始生成LaTeX数据, from_content_list, count={len(date_or_contents)}")
        else:
            logger.warning(f"开始生成LaTeX数据, 参数类型={type(date_or_contents).__name__}")

        # LaTeX 数据格式与 Typst 类似
        result = PublishService.generate_typst_data(date_or_contents)

        # 记录完成日志
        logger.info("LaTeX数据生成成功")

        return result
