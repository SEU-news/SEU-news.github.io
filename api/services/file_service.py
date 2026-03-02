"""
文件服务
处理文件上传、图片处理、URL粘贴等业务逻辑
"""

import os
import json
from datetime import datetime
from typing import List
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_models.models import User_info, Content
from api.core.exceptions import ValidationError, PermissionDeniedError
from api.config.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from api.services.base_service import BaseService


class FileService(BaseService):
    """文件服务类"""

    @staticmethod
    def validate_image_file(image_file: InMemoryUploadedFile) -> None:
        """
        验证图片文件

        Args:
            image_file: 上传的图片文件

        Raises:
            ValidationError: 文件验证失败
        """
        # 检查文件名
        if not image_file.name:
            raise ValidationError('文件名不能为空')

        # 检查文件扩展名
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}')

        # 检查文件大小
        if image_file.size > MAX_FILE_SIZE:
            raise ValidationError(f'文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024}MB)')

    @staticmethod
    def save_image_file(image_file: InMemoryUploadedFile, user_id: int) -> str:
        """
        保存图片文件

        Args:
            image_file: 上传的图片文件
            user_id: 用户ID

        Returns:
            保存的文件路径

        Raises:
            ValidationError: 文件验证失败
        """
        # 验证文件
        FileService.validate_image_file(image_file)

        # 创建上传目录
        upload_path = os.path.join(UPLOAD_DIR, f'user_{user_id}')
        os.makedirs(upload_path, exist_ok=True)

        # 生成唯一文件名
        ext = os.path.splitext(image_file.name)[1].lower()
        filename = f'{int(datetime.now().timestamp())}_{image_file.name}'
        filepath = os.path.join(upload_path, filename)

        # 保存文件
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 返回相对路径
        return os.path.join(UPLOAD_DIR, f'user_{user_id}', filename)

    @staticmethod
    def upload_image(image_file: InMemoryUploadedFile, user: User_info) -> str:
        """
        上传单个图片

        Args:
            image_file: 上传的图片文件
            user: 当前用户

        Returns:
            图片URL路径

        Raises:
            PermissionDeniedError: 无权限上传
            ValidationError: 文件验证失败
        """
        # 权限检查
        if not user.has_editor_perm:
            raise PermissionDeniedError('需要编辑权限才能上传图片')

        # 保存图片
        from datetime import datetime
        image_path = FileService.save_image_file(image_file, user.id)

        return f'/static/{image_path}'

    @staticmethod
    def upload_multiple_images(image_files: List[InMemoryUploadedFile], user: User_info) -> List[str]:
        """
        上传多个图片

        Args:
            image_files: 上传的图片文件列表
            user: 当前用户

        Returns:
            图片URL路径列表

        Raises:
            PermissionDeniedError: 无权限上传
            ValidationError: 文件验证失败
        """
        # 权限检查
        if not user.has_editor_perm:
            raise PermissionDeniedError('需要编辑权限才能上传图片')

        # 上传所有图片
        image_urls = []
        for image_file in image_files:
            url = FileService.upload_image(image_file, user)
            image_urls.append(url)

        return image_urls

    @staticmethod
    def add_image_to_content(content: Content, image_path: str) -> str:
        """
        将图片路径添加到内容的图片列表

        Args:
            content: 内容对象
            image_path: 图片路径

        Returns:
            更新后的图片列表JSON字符串

        Raises:
            ValidationError: 参数验证失败
        """
        if not image_path:
            raise ValidationError('图片路径不能为空')

        # 解析现有的图片列表
        try:
            if content.image_list and content.image_list != '[]':
                image_list = json.loads(content.image_list)
            else:
                image_list = []
        except json.JSONDecodeError:
            image_list = []

        # 添加新图片
        image_list.append(image_path)

        # 保存
        content.image_list = json.dumps(image_list)
        content.save(update_fields=['image_list'])

        return content.image_list

    @staticmethod
    def create_content_from_url(url: str, user: User_info) -> Content:
        """
        从URL创建内容（粘贴功能）

        Args:
            url: 粘贴的URL
            user: 当前用户

        Returns:
            新创建的内容对象

        Raises:
            PermissionDeniedError: 无权限创建
            ValidationError: URL验证失败
        """
        # 权限检查
        if not user.has_editor_perm:
            raise PermissionDeniedError('需要编辑权限才能粘贴URL')

        # 验证URL
        if not url or not url.startswith('http'):
            raise ValidationError('无效的URL')

        # 创建内容
        from api.services.content_service import ContentService
        data = {
            'title': url,  # 默认使用URL作为标题
            'content': f'来自URL: {url}',
            'link': url,
            'type': '其他',
            'status': 'draft',
        }

        content = ContentService.create_content(user, data)

        return content
