import logging
import sys

from django.conf import settings

from config.load_config import GLOBAL_CONFIG


def configure_django():
    """
    配置Django运行环境和数据库连接参数

    该函数读取数据库凭证信息并配置Django的数据库连接，包括MySQL连接参数、
    时区设置、安全密钥等必要配置项，使Django能够在独立环境中运行。
    """
    if not settings.configured:
        logger=logging.getLogger('initial')
        try:
            # 读取数据库用户凭证信息
            username = GLOBAL_CONFIG.get_config_value("MYSQL_username")
            password = GLOBAL_CONFIG.get_config_value("MYSQL_password")
            logger.info(f"[Database] Login with User: {username}")

            # 配置Django设置，包括数据库连接、已安装应用和基本配置
            settings.configure(
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "seu_news",
                        'USER': username,
                        'PASSWORD': password,
                        'HOST': 'localhost',  # 或者 '127.0.0.1'
                        'PORT': '3306',  # 默认 MySQL 端口
                        'OPTIONS': {
                            'charset': 'utf8mb4',
                            'unix_socket': '/var/run/mysqld/mysqld.sock',
                        }
                    }
                },
                INSTALLED_APPS=[
                    'django_models',  # 你的模型应用
                ],
                USE_TZ=False,
                SECRET_KEY="django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5",  # 建议改为从环境变量读取
                DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
            )
        except Exception as e:
            logger.error(f"[Database] Failed to configure Django: {e}")
            sys.exit(1)