"""
统一日志配置

提供项目统一的日志配置功能。
"""

import logging
import os
import sys
from logging import config
from pathlib import Path
from datetime import datetime

from .formatters import CustomFormatter
from .handlers import RotatingFileHandlerWithBackup


def setup_logging(
    log_dir: str = 'logs',
    log_level: str = 'DEBUG',
    console_level: str = 'INFO',
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 30,
) -> None:
    """
    配置项目的全局日志系统，同时输出到控制台和文件，并支持日志轮转。

    Args:
        log_dir: 日志目录路径
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_level: 控制台日志级别
        max_bytes: 单个日志文件最大字节数，默认 10MB
        backup_count: 保留的备份文件数量，默认 30 天
    """
    # 确保日志目录存在
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 获取项目根目录（相对于此文件的绝对路径）
    project_root = Path(__file__).parent.parent.parent

    # 定义日志文件路径
    app_log = log_path / 'app.log'
    error_log = log_path / 'error.log'

    # 定义日志配置字典
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,  # 允许其他模块的日志器正常工作
        'formatters': {
            'standard': {
                'format': '%(levelname)s - %(asctime)s - [%(name)s] - [%(filename)s:%(lineno)d] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '%(levelname)s - %(asctime)s - [%(name)s] - [%(filename)s:%(lineno)d] - [%(funcName)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': console_level,
                'formatter': 'standard',
                'stream': sys.stdout,
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': str(app_log.absolute()),
                'encoding': 'utf-8',
                'maxBytes': max_bytes,
                'backupCount': backup_count,
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': str(error_log.absolute()),
                'encoding': 'utf-8',
                'maxBytes': max_bytes,
                'backupCount': backup_count,
            },
        },
        'loggers': {
            # API 模块日志配置
            'api': {
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            # Django 日志配置
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            # 数据库查询日志
            'django.db.backends': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console', 'file', 'error_file'],
            'level': log_level,
        },
    }

    # 应用配置
    config.dictConfig(logging_config)

    # 记录日志系统启动信息
    logger = logging.getLogger(__name__)
    logger.info('=' * 60)
    logger.info('日志系统已初始化')
    logger.info(f'日志目录: {log_path.absolute()}')
    logger.info(f'日志级别: {log_level}')
    logger.info(f'控制台级别: {console_level}')
    logger.info(f'日志文件: {app_log.absolute()}')
    logger.info(f'错误日志: {error_log.absolute()}')
    logger.info(f'文件大小限制: {max_bytes / 1024 / 1024:.1f} MB')
    logger.info(f'保留天数: {backup_count} 天')
    logger.info('=' * 60)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器实例（与 logging.getLogger(__name__) 相同）

    Args:
        name: 日志器名称，通常使用 __name__

    Returns:
        日志器实例
    """
    return logging.getLogger(name)
