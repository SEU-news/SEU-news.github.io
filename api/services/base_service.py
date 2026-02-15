"""
基础服务类
提供所有服务的通用功能
"""

from typing import Optional, Dict, Any, List
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from api.core.exceptions import ValidationError, NotFoundError, BusinessLogicError


class BaseService:
    """基础服务类 - 提供通用方法"""

    @staticmethod
    def paginate(queryset, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        分页查询集

        Args:
            queryset: Django QuerySet
            page: 页码（从 1 开始）
            page_size: 每页条数

        Returns:
            分页结果字典
        """
        paginator = Paginator(queryset, page_size)

        try:
            paginated_queryset = paginator.page(page)
        except PageNotAnInteger:
            paginated_queryset = paginator.page(1)
        except EmptyPage:
            paginated_queryset = paginator.page(paginator.num_pages)

        return {
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': list(paginated_queryset),
        }

    @staticmethod
    def validate_required(data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        验证必需字段

        Args:
            data: 数据字典
            required_fields: 必需字段列表

        Raises:
            ValidationError: 如果缺少必需字段
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationError(f'缺少必需字段: {", ".join(missing_fields)}')

    @staticmethod
    def get_object_or_404(model_class, object_id: int, error_message: str = '对象不存在'):
        """
        获取对象或抛出 404 错误

        Args:
            model_class: Django 模型类
            object_id: 对象 ID
            error_message: 错误消息

        Returns:
            模型实例

        Raises:
            NotFoundError: 如果对象不存在
        """
        try:
            return model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            raise NotFoundError(error_message)

    @staticmethod
    def transaction():
        """
        事务装饰器

        Usage:
            with BaseService.transaction():
                # 数据库操作
        """
        return transaction.atomic()
