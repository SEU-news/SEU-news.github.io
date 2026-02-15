"""
工具函数
提供常用的辅助函数
"""

from datetime import datetime
from typing import Any, Dict


def format_datetime(dt: datetime) -> str:
    """
    格式化日期时间

    Args:
        dt: datetime 对象

    Returns:
        格式化后的字符串 (MM-DD HH:MM)
    """
    if not dt:
        return ''
    return dt.strftime('%m-%d %H:%M')


def format_date(dt: datetime) -> str:
    """
    格式化日期

    Args:
        dt: datetime 对象

    Returns:
        格式化后的字符串 (YYYY-MM-DD)
    """
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d')


def get_client_ip(request) -> str:
    """
    获取客户端 IP 地址

    Args:
        request: Django request 对象

    Returns:
        IP 地址字符串
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def build_response(success: bool = True, message: str = '', data: Any = None, code: str = 'success') -> Dict[str, Any]:
    """
    构建标准 API 响应

    Args:
        success: 是否成功
        message: 响应消息
        data: 响应数据
        code: 响应代码

    Returns:
        标准格式的响应字典
    """
    response = {
        'success': success,
        'code': code,
    }

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    return response


def paginate_queryset(queryset, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    分页查询集

    Args:
        queryset: Django queryset
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        分页结果字典
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    验证必需字段

    Args:
        data: 数据字典
        required_fields: 必需字段列表

    Raises:
        ValidationError: 如果缺少必需字段
    """
    from api.core.exceptions import ValidationError

    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(f'缺少必需字段: {", ".join(missing_fields)}')
