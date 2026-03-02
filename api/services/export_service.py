"""
导出服务
处理文档生成（PDF、Typst、LaTeX）和导出数据获取
"""

from typing import Dict, Any, List, Union
import os
import logging
from datetime import datetime

from django.conf import settings
from django_models.models import Content
from django_models.models import User_info
from api.services.base_service import BaseService
from api.services.publish_service import PublishService
from api.services.pdf_service import PDFService
from api.core.exceptions import ValidationError

from api.logging import get_logger

logger = get_logger(__name__)


class ExportService(BaseService):
    """导出服务类"""

    @staticmethod
    def generate_pdf(date_str: str = None, content_ids: List[int] = None, user: User_info = None) -> Dict[str, Any]:
        """
        生成 PDF（支持按日期或按选中内容）

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，可选
            content_ids: 内容ID列表，可选
            user: 当前用户，用于日志记录

        Returns:
            PDF生成结果

        Raises:
            ValidationError: 参数验证失败
        """
        # 记录入口日志
        user_info = f"user={user.username if user else 'anonymous'}, user_id={user.id if user else None}" if user else "user=anonymous"
        mode = f"date={date_str}" if date_str else f"content_ids={content_ids}"
        logger.info(f"开始生成PDF, {user_info}, mode={mode}")

        try:
            # 复用 PDFService 的逻辑
            result = PDFService.generate_pdf_from_selection(date_str=date_str, content_ids=content_ids)

            # 记录成功日志
            logger.info(f"PDF生成成功, {user_info}, mode={mode}, output_path={result.get('pdf_path', 'N/A')}")
            return result

        except ValidationError as e:
            # 记录验证错误
            logger.warning(
                f"PDF生成参数验证失败, {user_info}, mode={mode}, error={str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            # 记录失败日志（包含完整堆栈）
            logger.error(
                f"PDF生成失败, {user_info}, mode={mode}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def generate_typst(date: str, user: User_info = None) -> Dict[str, Any]:
        """
        生成 Typst 格式文档

        Args:
            date: 日期字符串 (YYYY-MM-DD)
            user: 当前用户，用于日志记录

        Returns:
            Typst 数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 记录入口日志
        user_info = f"user={user.username if user else 'anonymous'}, user_id={user.id if user else None}" if user else "user=anonymous"
        logger.info(f"开始生成Typst格式文档, {user_info}, date={date}")

        try:
            # 使用 publish_utils.generate_typst_data 返回 Flask 格式
            from api.utils.publish_utils import generate_typst_data
            result = generate_typst_data(date)

            # 记录成功日志
            categories_count = sum(len(v) for v in result.get('categories', {}).values())
            logger.info(
                f"Typst格式文档生成成功, {user_info}, date={date}, "
                f"categories={len(result.get('categories', {}))}, items={categories_count}, "
                f"ddl_items={len(result.get('ddl_items', []))}"
            )
            return result

        except ValidationError as e:
            # 记录验证错误
            logger.warning(
                f"Typst生成参数验证失败, {user_info}, date={date}, error={str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            # 记录失败日志
            logger.error(
                f"Typst生成失败, {user_info}, date={date}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def generate_latex(date: str, user: User_info = None) -> Dict[str, Any]:
        """
        生成 LaTeX 格式文档

        Args:
            date: 日期字符串 (YYYY-MM-DD)
            user: 当前用户，用于日志记录

        Returns:
            LaTeX 数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 记录入口日志
        user_info = f"user={user.username if user else 'anonymous'}, user_id={user.id if user else None}" if user else "user=anonymous"
        logger.info(f"开始生成LaTeX格式文档, {user_info}, date={date}")

        try:
            # 使用 publish_utils.generate_typst_data 返回 Flask 格式
            from api.utils.publish_utils import generate_typst_data
            result = generate_typst_data(date)

            # 记录成功日志
            categories_count = sum(len(v) for v in result.get('categories', {}).values())
            logger.info(
                f"LaTeX格式文档生成成功, {user_info}, date={date}, "
                f"categories={len(result.get('categories', {}))}, items={categories_count}, "
                f"ddl_items={len(result.get('ddl_items', []))}"
            )
            return result

        except ValidationError as e:
            # 记录验证错误
            logger.warning(
                f"LaTeX生成参数验证失败, {user_info}, date={date}, error={str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            # 记录失败日志
            logger.error(
                f"LaTeX生成失败, {user_info}, date={date}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise

    @staticmethod
    def get_export_data(date: str, user: User_info = None) -> Dict[str, Any]:
        """
        获取导出数据（Flask 兼容格式）

        Args:
            date: 日期字符串 (YYYY-MM-DD)
            user: 当前用户，用于日志记录

        Returns:
            导出数据字典

        Raises:
            ValidationError: 日期格式错误
        """
        # 记录入口日志
        user_info = f"user={user.username if user else 'anonymous'}, user_id={user.id if user else None}" if user else "user=anonymous"
        logger.info(f"开始获取导出数据, {user_info}, date={date}")

        try:
            # 使用 publish_utils.generate_typst_data 返回 Flask 格式
            from api.utils.publish_utils import generate_typst_data
            result = generate_typst_data(date)

            # 记录成功日志
            categories_count = sum(len(v) for v in result.get('categories', {}).values())
            logger.info(
                f"导出数据获取成功, {user_info}, date={date}, "
                f"categories={len(result.get('categories', {}))}, items={categories_count}, "
                f"ddl_items={len(result.get('ddl_items', []))}"
            )
            return result

        except ValidationError as e:
            # 记录验证错误
            logger.warning(
                f"导出数据获取参数验证失败, {user_info}, date={date}, error={str(e)}",
                exc_info=True
            )
            raise
        except Exception as e:
            # 记录失败日志
            logger.error(
                f"导出数据获取失败, {user_info}, date={date}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise
