"""
日志上下文管理

提供线程安全的日志上下文管理功能，用于在日志中添加用户信息、请求 ID 等上下文。
"""

import logging
import threading
from typing import Optional, Dict, Any

# 线程本地存储
_local = threading.local()


class LogContext:
    """
    日志上下文管理器

    使用线程本地存储来管理日志上下文，确保每个线程的上下文互不干扰。
    """

    @staticmethod
    def set_user(user_id: int, username: str) -> None:
        """
        设置当前用户信息

        Args:
            user_id: 用户 ID
            username: 用户名
        """
        if not hasattr(_local, 'context'):
            _local.context = {}
        _local.context['user_id'] = user_id
        _local.context['username'] = username

    @staticmethod
    def set_request_id(request_id: str) -> None:
        """
        设置当前请求 ID

        Args:
            request_id: 请求唯一标识
        """
        if not hasattr(_local, 'context'):
            _local.context = {}
        _local.context['request_id'] = request_id

    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        设置自定义上下文

        Args:
            key: 上下文键
            value: 上下文值
        """
        if not hasattr(_local, 'context'):
            _local.context = {}
        _local.context[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        获取上下文值

        Args:
            key: 上下文键
            default: 默认值

        Returns:
            上下文值
        """
        if hasattr(_local, 'context'):
            return _local.context.get(key, default)
        return default

    @staticmethod
    def get_all() -> Dict[str, Any]:
        """
        获取所有上下文

        Returns:
            所有上下文键值对
        """
        if hasattr(_local, 'context'):
            return _local.context.copy()
        return {}

    @staticmethod
    def clear() -> None:
        """清空当前线程的上下文"""
        if hasattr(_local, 'context'):
            _local.context.clear()


class ContextualLogger(logging.Logger):
    """
    上下文感知日志器

    自动将当前上下文信息添加到日志消息中。
    """

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
        重写日志方法，自动添加上下文信息

        Args:
            level: 日志级别
            msg: 日志消息
            args: 消息参数
            exc_info: 异常信息
            extra: 额外信息
            stack_info: 堆栈信息
        """
        # 获取当前上下文
        context = LogContext.get_all()

        # 如果有上下文信息，添加到日志消息
        if context and extra is None:
            extra = {}

        if context and extra is not None:
            # 合并上下文到额外信息中
            extra.update({f'ctx_{k}': v for k, v in context.items()})

        super()._log(level, msg, args, exc_info, extra, stack_info)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器实例

    此函数与 logging.getLogger(__name__) 功能相同，提供统一的接口。

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        日志器实例
    """
    return logging.getLogger(name)


def setup_context_logging():
    """
    设置上下文日志系统

    将自定义的 ContextualLogger 设置为默认的日志器类。
    """
    logging.setLoggerClass(ContextualLogger)
