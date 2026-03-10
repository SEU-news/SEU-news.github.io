"""
内容服务
处理内容的创建、更新、审核、撤回等业务逻辑
"""

from typing import Dict, Any, List
from django.db.models import Q
from api.django_models import User_info, Content
from api.core.exceptions import ValidationError, PermissionDeniedError, NotFoundError, BusinessLogicError
from api.config.constants import CONTENT_STATUS_PUBLISHED
from api.services.base_service import BaseService
from api.logging import get_logger
import json


logger = get_logger(__name__)


class ContentService(BaseService):
    """内容服务类"""

    @staticmethod
    def create_content(creator: User_info, data: Dict[str, Any]) -> Content:
        """
        创建内容

        Args:
            creator: 创建者用户对象
            data: 内容数据

        Returns:
            新创建的内容对象

        Raises:
            ValidationError: 参数验证失败
        """
        # 记录入口日志
        user_info = f"user={creator.username}, user_id={creator.id}"
        title = data.get('title', 'N/A')
        type_ = data.get('type', 'N/A')
        logger.info(f"开始创建内容, {user_info}, title={title}, type={type_}")

        try:
            # 验证必需字段
            required_fields = ['title', 'content', 'type']
            ContentService.validate_required(data, required_fields)

            # 提取数据
            title = data['title']
            content = data['content']
            type_ = data['type']
            link = data.get('link', '')
            short_title = data.get('short_title', '')

            # 处理标签（支持数组或字符串）
            tag = ContentService._process_tag(data.get('tag', ''))

            deadline = data.get('deadline')

            # 验证内容类型
            from api.config.constants import CONTENT_TYPES
            if type_ not in CONTENT_TYPES:
                logger.warning(
                    f"内容创建失败: 无效的内容类型, {user_info}, "
                    f"type={type_}, valid_types={', '.join(CONTENT_TYPES)}",
                    exc_info=True
                )
                raise ValidationError(f'无效的内容类型，必须是: {", ".join(CONTENT_TYPES)}')

            # 创建内容
            with BaseService.transaction():
                content_obj = Content.objects.create(
                    creator_id=creator.id,
                    describer_id=creator.id,  # 默认为创建者
                    title=title,
                    content=content,
                    link=link,
                    type=type_,
                    short_title=short_title,
                    tag=tag,
                    deadline=deadline,
                    status='draft',
                    image_list='[]',
                )

            # 记录成功日志
            logger.info(
                f"内容创建成功, {user_info}, content_id={content_obj.id}, "
                f"title={title}, type={type_}, status={content_obj.status}"
            )
            return content_obj

        except ValidationError as e:
            # 验证错误已在上面处理，这里记录警告
            logger.warning(f"内容创建验证失败, {user_info}, error={str(e)}", exc_info=True)
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容创建失败, {user_info}, title={title}, type={type_}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def update_content(content: Content, data: Dict[str, Any], user: User_info) -> Content:
        """
        更新内容

        Args:
            content: 内容对象
            data: 更新数据
            user: 当前用户

        Returns:
            更新后的内容对象

        Raises:
            PermissionDeniedError: 无权限修改
            ValidationError: 参数验证失败
        """
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        content_info = f"content_id={content.id}, title={content.title}, status={content.status}"
        update_fields = list(data.keys())
        logger.info(f"开始更新内容, {user_info}, {content_info}, fields={update_fields}")

        try:
            # 权限检查：只有创建者和管理员可以修改
            if content.creator_id != user.id and not user.has_admin_perm:
                logger.warning(
                    f"内容更新失败: 无权限, {user_info}, {content_info}",
                    exc_info=True
                )
                raise PermissionDeniedError('只有内容创建者或管理员可以修改')

            # 状态检查：只有草稿和已拒绝状态可以修改
            if content.status not in ['draft', 'rejected']:
                logger.warning(
                    f"内容更新失败: 状态不允许修改, {user_info}, {content_info}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许修改')

            # 允许更新的字段
            allowed_fields = ['title', 'short_title', 'content', 'link', 'type', 'tag', 'deadline']

            # 更新字段
            for field in allowed_fields:
                if field in data:
                    # 特殊处理 tag 字段
                    if field == 'tag':
                        setattr(content, field, ContentService._process_tag(data[field]))
                    else:
                        setattr(content, field, data[field])

            content.save()

            # 记录成功日志
            logger.info(f"内容更新成功, {user_info}, {content_info}, updated_fields={update_fields}")
            return content

        except (PermissionDeniedError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容更新失败, {user_info}, {content_info}, fields={update_fields}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def describe_content(content_id: int, describer: User_info) -> Content:
        """
        描述内容（提交审核）

        Args:
            content_id: 内容ID
            describer: 描述者用户对象

        Returns:
            更新后的内容对象

        Raises:
            NotFoundError: 内容不存在
            BusinessLogicError: 状态不允许描述
        """
        # 记录入口日志
        user_info = f"user={describer.username}, user_id={describer.id}"
        logger.info(f"开始描述内容, {user_info}, content_id={content_id}")

        try:
            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 状态检查
            if content.status != 'draft':
                logger.warning(
                    f"内容描述失败: 状态不允许, {user_info}, content_id={content_id}, "
                    f"current_status={content.status}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许提交描述')

            # 更新为待审核状态
            content.describer_id = describer.id
            content.status = 'pending'
            content.save()

            # 记录成功日志
            logger.info(
                f"内容描述成功, {user_info}, content_id={content_id}, "
                f"title={content.title}, new_status=pending"
            )
            return content

        except (NotFoundError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容描述失败, {user_info}, content_id={content_id}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def submit_content(content_id: int, submitter: User_info) -> Content:
        """
        提交内容审核（纯状态转换）

        设计说明：
        - submitter（提交者）≠ describer（描述者）
        - 提交者只是执行"提交审核"动作的人
        - describer_id 保持不变，由真正描述内容的人决定
        - 此方法只改变状态，不修改 describer_id

        Args:
            content_id: 内容ID
            submitter: 提交者用户对象

        Returns:
            更新后的内容对象

        Raises:
            NotFoundError: 内容不存在
            BusinessLogicError: 状态不允许提交
            PermissionDeniedError: 无权限提交
        """
        # 记录入口日志
        user_info = f"user={submitter.username}, user_id={submitter.id}"
        logger.info(f"开始提交内容审核, {user_info}, content_id={content_id}")

        try:
            # 权限检查：需要编辑权限
            if not submitter.has_editor_perm:
                logger.warning(
                    f"内容提交失败: 无权限, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise PermissionDeniedError('需要编辑权限才能提交审核')

            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 状态检查：只有草稿可以提交
            if content.status != 'draft':
                logger.warning(
                    f"内容提交失败: 状态不允许, {user_info}, content_id={content_id}, "
                    f"current_status={content.status}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许提交审核')

            # 更新为待审核状态（不修改 describer_id）
            old_status = content.status
            content.status = 'pending'
            content.save()

            # 记录成功日志
            logger.info(
                f"内容提交成功, {user_info}, content_id={content_id}, "
                f"title={content.title}, old_status={old_status}, new_status=pending, "
                f"describer_id={content.describer_id}"
            )
            return content

        except (PermissionDeniedError, NotFoundError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容提交失败, {user_info}, content_id={content_id}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def review_content(content_id: int, reviewer: User_info, approved: bool, comment: str = '') -> Content:
        """
        审核内容

        Args:
            content_id: 内容ID
            reviewer: 审核者用户对象
            approved: 是否通过
            comment: 审核意见

        Returns:
            更新后的内容对象

        Raises:
            NotFoundError: 内容不存在
            PermissionDeniedError: 无权限审核
            BusinessLogicError: 状态不允许审核或不能审核自己的内容
        """
        # 记录入口日志
        user_info = f"user={reviewer.username}, user_id={reviewer.id}"
        action = "通过" if approved else "拒绝"
        logger.info(f"开始审核内容, {user_info}, content_id={content_id}, action={action}")

        try:
            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 权限检查：需要编辑权限
            if not reviewer.has_editor_perm:
                logger.warning(
                    f"内容审核失败: 无权限, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise PermissionDeniedError('需要编辑权限才能审核')

            # 不能审核自己的内容
            if content.creator_id == reviewer.id:
                logger.warning(
                    f"内容审核失败: 不能审核自己的内容, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise BusinessLogicError('不能审核自己创建的内容')

            # 状态检查
            if content.status != 'pending':
                logger.warning(
                    f"内容审核失败: 状态不允许, {user_info}, content_id={content_id}, "
                    f"current_status={content.status}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许审核')

            # 更新状态
            old_status = content.status
            content.reviewer_id = reviewer.id
            new_status = 'reviewed' if approved else 'rejected'
            content.status = new_status
            content.save()

            # 记录成功日志
            logger.info(
                f"内容审核成功, {user_info}, content_id={content_id}, title={content.title}, "
                f"old_status={old_status}, new_status={new_status}, comment={comment}"
            )
            return content

        except (PermissionDeniedError, NotFoundError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容审核失败, {user_info}, content_id={content_id}, action={action}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def recall_content(content_id: int, user: User_info) -> Content:
        """
        撤回内容（创建者或管理员可以将已发布的内容撤回）

        Args:
            content_id: 内容ID
            user: 当前用户

        Returns:
            更新后的内容对象

        Raises:
            NotFoundError: 内容不存在
            PermissionDeniedError: 无权限撤回
            BusinessLogicError: 状态不允许撤回
        """
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        logger.info(f"开始撤回内容, {user_info}, content_id={content_id}")

        try:
            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 权限检查
            if content.creator_id != user.id and not user.has_admin_perm:
                logger.warning(
                    f"内容撤回失败: 无权限, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise PermissionDeniedError('只有内容创建者或管理员可以撤回')

            # 状态检查
            if content.status not in [CONTENT_STATUS_PUBLISHED, 'reviewed', 'pending']:
                logger.warning(
                    f"内容撤回失败: 状态不允许, {user_info}, content_id={content_id}, "
                    f"current_status={content.status}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许撤回')

            # 撤回到草稿状态
            old_status = content.status
            content.status = 'draft'
            content.reviewer_id = None
            content.save()

            # 记录成功日志
            logger.info(
                f"内容撤回成功, {user_info}, content_id={content_id}, title={content.title}, "
                f"old_status={old_status}, new_status=draft"
            )
            return content

        except (PermissionDeniedError, NotFoundError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容撤回失败, {user_info}, content_id={content_id}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def cancel_content(content_id: int, user: User_info) -> bool:
        """
        取消内容（创建者可以取消自己的内容）

        Args:
            content_id: 内容ID
            user: 当前用户

        Returns:
            是否成功取消

        Raises:
            NotFoundError: 内容不存在
            PermissionDeniedError: 无权限取消
            BusinessLogicError: 状态不允许取消
        """
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        logger.info(f"开始取消内容, {user_info}, content_id={content_id}")

        try:
            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 权限检查：只有创建者和管理员可以取消
            if content.creator_id != user.id and not user.has_admin_perm:
                logger.warning(
                    f"内容取消失败: 无权限, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise PermissionDeniedError('只有内容创建者或管理员可以取消')

            # 状态检查
            if content.status in ['published', 'terminated']:
                logger.warning(
                    f"内容取消失败: 状态不允许, {user_info}, content_id={content_id}, "
                    f"current_status={content.status}",
                    exc_info=True
                )
                raise BusinessLogicError(f'当前状态({content.status})不允许取消')

            # 取消（终止）内容
            old_status = content.status
            content.status = 'terminated'
            content.save()

            # 记录成功日志
            logger.info(
                f"内容取消成功, {user_info}, content_id={content_id}, title={content.title}, "
                f"old_status={old_status}, new_status=terminated"
            )
            return True

        except (PermissionDeniedError, NotFoundError, BusinessLogicError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容取消失败, {user_info}, content_id={content_id}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def delete_content(content_id: int, user: User_info) -> bool:
        """
        删除内容

        Args:
            content_id: 内容ID
            user: 当前用户

        Returns:
            是否成功删除

        Raises:
            NotFoundError: 内容不存在
            PermissionDeniedError: 无权限删除
        """
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        logger.info(f"开始删除内容, {user_info}, content_id={content_id}")

        try:
            content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

            # 权限检查：只有创建者和管理员可以删除
            if content.creator_id != user.id and not user.has_admin_perm:
                logger.warning(
                    f"内容删除失败: 无权限, {user_info}, content_id={content_id}",
                    exc_info=True
                )
                raise PermissionDeniedError('只有内容创建者或管理员可以删除')

            # 删除前记录内容信息
            content_title = content.title
            content_status = content.status

            content.delete()

            # 记录成功日志
            logger.info(
                f"内容删除成功, {user_info}, content_id={content_id}, "
                f"title={content_title}, status={content_status}"
            )
            return True

        except (PermissionDeniedError, NotFoundError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容删除失败, {user_info}, content_id={content_id}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def search_content(query: str, user: User_info) -> List[Content]:
        """
        搜索内容

        Args:
            query: 搜索关键词
            user: 当前用户

        Returns:
            搜索结果列表

        Raises:
            ValidationError: 参数验证失败
            PermissionDeniedError: 无权限搜索
        """
        # 记录入口日志
        user_info = f"user={user.username}, user_id={user.id}"
        logger.info(f"开始搜索内容, {user_info}, query={query}")

        try:
            # 权限检查
            if not user.has_editor_perm:
                logger.warning(
                    f"内容搜索失败: 无权限, {user_info}, query={query}",
                    exc_info=True
                )
                raise PermissionDeniedError('需要编辑权限才能搜索')

            # 验证参数
            if not query or len(query) < 1:
                logger.warning(
                    f"内容搜索失败: 参数无效, {user_info}, query={query}",
                    exc_info=True
                )
                raise ValidationError('搜索关键词至少为 1 个字符')

            # 搜索标题和内容
            results = Content.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).order_by('-created_at')

            result_list = list(results)

            # 记录成功日志
            logger.info(
                f"内容搜索成功, {user_info}, query={query}, result_count={len(result_list)}"
            )
            return result_list

        except (PermissionDeniedError, ValidationError) as e:
            # 业务逻辑错误已在上面处理
            raise
        except Exception as e:
            # 记录其他错误
            logger.error(
                f"内容搜索失败, {user_info}, query={query}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def _process_tag(tag_input):
        """
        处理标签输入，统一转换为 JSON 数组字符串格式

        Args:
            tag_input: 标签输入，支持以下格式：
                - 字符串: "标签1,标签2,标签3"
                - 数组: ["标签1", "标签2", "标签3"]
                - 空值: "" 或 []

        Returns:
            JSON 数组字符串: '["标签1","标签2","标签3"]'
        """
        # 如果是空值，返回空数组
        if not tag_input:
            return '[]'

        # 如果已经是 JSON 数组字符串，直接返回
        if isinstance(tag_input, str) and tag_input.startswith('['):
            try:
                # 验证是否为有效的 JSON
                json.loads(tag_input)
                return tag_input
            except json.JSONDecodeError:
                pass

        # 如果是列表，转换为 JSON 数组字符串
        if isinstance(tag_input, list):
            return json.dumps(tag_input, ensure_ascii=False)

        # 如果是字符串，按逗号分割后转换为 JSON 数组
        if isinstance(tag_input, str):
            tags = [t.strip() for t in tag_input.split(',') if t.strip()]
            return json.dumps(tags, ensure_ascii=False)

        # 其他情况返回空数组
        return '[]'

    @staticmethod
    def admin_update_status(content_id: int, admin: User_info, new_status: str, reason: str = '') -> Content:
        """
        管理员强制更新内容状态

        Args:
            content_id: 内容ID
            admin: 管理员用户对象
            new_status: 新状态值
            reason: 状态变更原因（用于审计）

        Returns:
            更新后的内容对象

        Raises:
            NotFoundError: 内容不存在
            PermissionDeniedError: 非管理员
            ValidationError: 无效的状态值
        """
        # 验证权限（角色必须是管理员）
        if not admin.has_admin_permission():
            raise PermissionDeniedError('只有管理员可以强制修改内容状态')

        # 获取内容对象
        content = ContentService.get_object_or_404(Content, content_id, '内容不存在')

        # 严格的状态验证
        valid_statuses = [status for status, _ in Content.STATUS_CHOICES]
        if new_status not in valid_statuses:
            raise ValidationError(f'无效的状态值，必须是: {", ".join(valid_statuses)}')

        # 记录旧状态
        old_status = content.status

        # 更新状态
        content.status = new_status
        content.save()

        # 审计日志
        logger.info(
            f'超级管理员强制修改状态: content_id={content_id}, '
            f'old_status={old_status}, new_status={new_status}, '
            f'admin={admin.username}, reason={reason}'
        )

        return content
