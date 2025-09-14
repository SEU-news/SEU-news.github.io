import logging
import os
import sys

import django

from django_config import configure_django


if __name__ == '__main__':
    # 配置日志系统
    try:
        # 确保日志目录存在
        log_file = 'app.log'
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s - %(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        logging.error(f"Failed to configure logging: {e}")
        sys.exit(1)
    else:
        logging.info("Logging configured successfully")

    try:
        configure_django()
        django.setup()
    except Exception as e:
        logging.error(f"Failed to initialize Django: {e}")
        sys.exit(1)
    else:
        logging.info("Django initialized successfully")

    # 从环境变量获取端口，如果没有则使用默认值
    port = int(os.environ.get('APP_PORT', 42610))
    logging.info(f"Starting server on port {port}")

    from apis_flask import app
    app.run(host="0.0.0.0", debug=False, port=port)
