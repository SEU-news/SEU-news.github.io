"""
日志格式化器

提供自定义的日志格式化功能。
"""

import logging
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """
    自定义日志格式化器

    提供更灵活的日志格式化选项，支持：
    - 彩色输出（控制台）
    - 额外的上下文信息
    """

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'

    def __init__(self, fmt: str = None, datefmt: str = None, use_color: bool = True):
        """
        初始化格式化器

        Args:
            fmt: 日志格式字符串
            datefmt: 日期格式字符串
            use_color: 是否使用彩色输出
        """
        super().__init__(fmt, datefmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录

        Args:
            record: 日志记录对象

        Returns:
            格式化后的日志字符串
        """
        levelname = record.levelname

        # 添加颜色（如果启用且是控制台输出）
        if self.use_color and levelname in self.COLORS:
            color = self.COLORS[levelname]
            record.levelname = f'{color}{levelname}{self.RESET}'

        # 调用父类格式化
        result = super().format(record)

        # 恢复原始 levelname（避免颜色代码累积）
        record.levelname = levelname

        return result


class DetailedFormatter(logging.Formatter):
    """
    详细日志格式化器

    用于错误日志，包含更多上下文信息。
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录（包含详细信息）

        Args:
            record: 日志记录对象

        Returns:
            格式化后的日志字符串
        """
        # 添加额外的信息
        if record.exc_info:
            # 如果有异常信息，添加进程和线程信息
            result = super().format(record)
            result += f'\n  Process: {record.processName} (PID: {record.process})'
            result += f'\n  Thread: {record.threadName} (TID: {record.thread})'
            return result
        else:
            return super().format(record)
