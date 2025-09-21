import logging
import os
import sys

import django

from apis.errHandler import register_error_handlers
from config.django_config import configure_django
from config.load_config import GLOBAL_CONFIG
from loggers import setup_global_logging

if __name__ == '__main__':
    # 配置日志系统
    try:
        setup_global_logging()
    except Exception as e:
        logging.error(f"[Logging] 日志配置失败: {e}")
        sys.exit(1)
    else:
        init_logger = logging.getLogger('initial')
        init_logger.info("[Logging] 日志系统配置成功")

    try:
        configure_django()
        django.setup()
    except Exception as e:
        init_logger.error(f"Django初始化失败: {e}")
        sys.exit(1)
    else:
        init_logger.info("Django初始化成功")

    # 从环境变量获取端口，如果没有则使用默认值
    port = int(os.environ.get('APP_PORT', 42610))
    init_logger.info(f"正在启动服务器，端口: {port}")
    from API_register import create_app

    app = create_app()
    register_error_handlers(app)
    env = GLOBAL_CONFIG.get_config_value("env", "test")
    if env == "prod":
        app.run(host="0.0.0.0", debug=False, port=port)
    else:
        app.run(host="0.0.0.0", debug=True, port=port)
