import logging
from datetime import datetime

from common.content_status import ContentStatus
from django_models.models import User_info, Content


class ContentService:
    """内容服务类，提供内容相关的通用操作方法"""

    _logger = logging.getLogger(__name__)

    @staticmethod
    def create(title, content_text, username, type, short_title=None, due_time=None, tag='', link=''):
        """
        创建新内容的通用方法

        Args:
            title (str): 内容标题
            content_text (str): 内容文本
            username (str): 创建者用户名
            type (str): 内容类型
            short_title (str, optional): 短标题，默认为None
            due_time (str, optional): 截止时间，默认为None
            tag (str, optional): 标签，默认为空字符串
            link (str, optional): 链接地址，默认为空字符串

        Returns:
            Content: 创建的内容对象

        Raises:
            User_info.DoesNotExist: 当指定用户不存在时抛出异常
            ValueError: 当截止时间格式不正确时抛出异常
        """
        # 获取当前登录用户信息
        try:
            user = User_info.objects.get(username=username)
        except User_info.DoesNotExist:
            raise User_info.DoesNotExist('User does not exist')

        # 处理截止时间，支持两种格式: YYYY-MM-DD 或 ISO标准格式
        deadline_value = None
        if due_time:
            try:
                if len(due_time) == 10:  # "YYYY-MM-DD"格式
                    deadline_value = datetime.strptime(due_time, '%Y-%m-%d')
                else:  # ISO标准格式
                    deadline_value = datetime.fromisoformat(due_time)
            except ValueError:
                raise ValueError('Invalid date format for deadline')

        # 如果没有设置截止时间，则设置为默认远期时间
        if deadline_value is None:
            deadline_value = datetime(2099, 12, 31)

        # 如果没有提供短标题，则使用标题作为短标题
        if not short_title:
            short_title = title

        status = ContentStatus("draft")

        # 创建新的内容记录
        content = Content.objects.create(
            creator_id=user.id,
            describer_id=user.id,
            title=title,
            short_title=short_title,
            content=content_text,
            link=link,
            status=status.string_en(),
            type=type,
            tag=tag,
            deadline=deadline_value,
            publish_at=datetime.now()
        )

        # 记录内容创建操作的日志
        ContentService._logger.info(f"用户 {user.username} 创建了新内容: {title}")

        return content