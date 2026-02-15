"""
导出服务
处理文档生成（PDF、Typst、LaTeX）和导出数据获取
"""

from typing import Dict, Any, List, Union
import os
from datetime import datetime

from django.conf import settings
from django_models.models import Content
from api.services.base_service import BaseService
from api.services.publish_service import PublishService
from api.services.pdf_service import PDFService
from api.core.exceptions import ValidationError


class ExportService(BaseService):
    """导出服务类"""

    @staticmethod
    def generate_pdf(date_str: str = None, content_ids: List[int] = None) -> Dict[str, Any]:
        """
        生成 PDF（支持按日期或按选中内容）

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，可选
            content_ids: 内容ID列表，可选

        Returns:
            PDF生成结果

        Raises:
            ValidationError: 参数验证失败
        """
        # 复用 PDFService 的逻辑
        return PDFService.generate_pdf_from_selection(date_str=date_str, content_ids=content_ids)

    @staticmethod
    def generate_typst(date: str) -> Dict[str, Any]:
        """
        生成 Typst 格式文档

        Args:
            date: 日期字符串 (YYYY-MM-DD)

        Returns:
            Typst 数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 使用 publish_utils.generate_typst_data 返回 Flask 格式
        from api.utils.publish_utils import generate_typst_data
        return generate_typst_data(date)

    @staticmethod
    def generate_latex(date: str) -> Dict[str, Any]:
        """
        生成 LaTeX 格式文档

        Args:
            date: 日期字符串 (YYYY-MM-DD)

        Returns:
            LaTeX 数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 使用 publish_utils.generate_typst_data 返回 Flask 格式
        from api.utils.publish_utils import generate_typst_data
        return generate_typst_data(date)

    @staticmethod
    def get_export_data(date: str) -> Dict[str, Any]:
        """
        获取导出数据（Flask 兼容格式）

        Args:
            date: 日期字符串 (YYYY-MM-DD)

        Returns:
            导出数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 使用 publish_utils.generate_typst_data 返回 Flask 格式
        from api.utils.publish_utils import generate_typst_data
        return generate_typst_data(date)
