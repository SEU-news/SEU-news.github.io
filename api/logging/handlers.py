"""
日志处理器

提供自定义的日志处理功能。
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path


class RotatingFileHandlerWithBackup(RotatingFileHandler):
    """
    支持按日期和大小双重轮转的日志处理器

    结合了 RotatingFileHandler 和 TimedRotatingFileHandler 的功能：
    - 按大小轮转：当文件达到指定大小时创建新文件
    - 按日期备份：备份文件名包含日期信息
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        """
        初始化处理器

        Args:
            filename: 日志文件路径
            mode: 文件打开模式
            maxBytes: 文件最大字节数
            backupCount: 保留的备份文件数量
            encoding: 文件编码
            delay: 是否延迟打开文件
        """
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.baseFilename = filename
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def doRollover(self):
        """
        执行日志轮转

        覆盖父类方法，在备份文件名中添加日期信息。
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # 获取当前日期
        current_date = datetime.now().strftime('%Y-%m-%d')

        # 重命名现有文件，添加日期后缀
        base, ext = os.path.splitext(self.baseFilename)
        for i in range(self.backupCount, 0, -1):
            sfn = f"{base}.{current_date}.{i}{ext}"
            if i == 1:
                # 第一个备份文件是当前日志
                if os.path.exists(self.baseFilename):
                    os.rename(self.baseFilename, sfn)
            else:
                # 后续备份文件
                next_sfn = f"{base}.{current_date}.{i - 1}{ext}"
                if os.path.exists(next_sfn):
                    os.rename(next_sfn, sfn)

        # 打开新文件
        if not self.delay:
            self.stream = self._open()


class ContextFilter(logging.Filter):
    """
    上下文过滤器

    可以在日志中添加额外的上下文信息，如用户 ID、请求 ID 等。
    """

    def __init__(self):
        super().__init__()
        self.context = {}

    def add_context(self, key: str, value: any) -> None:
        """
        添加上下文信息

        Args:
            key: 上下文键
            value: 上下文值
        """
        self.context[key] = value

    def clear_context(self) -> None:
        """清空上下文信息"""
        self.context.clear()

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录，添加上下文信息

        Args:
            record: 日志记录对象

        Returns:
            是否记录此日志
        """
        # 将上下文信息添加到日志记录
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


# 全局上下文过滤器实例
context_filter = ContextFilter()
