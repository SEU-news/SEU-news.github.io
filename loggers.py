import logging
import os
import sys
from logging import config


def setup_global_logging(log_file: str = 'app.log') -> None:
    """
    配置项目的全局日志系统，同时输出到控制台和文件，并避免重复记录。

    Args:
        log_file: 日志文件路径。
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(os.path.abspath(log_file))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 定义日志配置字典
    logging_config: dict[str, any] = {
        'version': 1,
        'disable_existing_loggers': False,  # 非常重要：允许其他模块的日志器正常工作[4](@ref)
        'formatters': {
            'standard': {
                'format': '%(levelname)s - %(asctime)s - [%(name)s] - [%(filename)s:%(lineno)d] - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',  # 控制台输出INFO及以上级别
                'formatter': 'standard',
                'stream': sys.stdout,
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',  # 文件记录DEBUG及以上级别
                'formatter': 'standard',
                'filename': log_file,
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            # 可以在此为特定模块或日志器配置更细致的行为
            'initial': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,  # 防止向上传播到根日志器，避免重复
            },
            'api_manage': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,  # 防止向上传播到根日志器，避免重复
            },
        },
        'root': {  # 根日志器配置，捕获所有未在'loggers'中显式配置的日志器
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    }

    # 应用配置
    logging.config.dictConfig(logging_config)
