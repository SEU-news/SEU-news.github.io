"""
统一日志模块

提供项目统一的日志配置和管理功能。

使用示例:
    from api.logging import setup_logging, get_logger

    # 初始化日志系统
    setup_logging()

    # 获取日志器
    logger = get_logger(__name__)
    logger.info("这是一条信息日志")
"""

from .config import setup_logging
from .context import get_logger

__all__ = [
    'setup_logging',
    'get_logger',
]
