import logging
import os
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
                # 开发模式配置
                DEBUG=True,  # 开发环境设为 True

                # 允许的主机
                ALLOWED_HOSTS=[
                    '0.0.0.0',
                    'localhost',
                    '127.0.0.1',
                ],

                INSTALLED_APPS=[
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'django.contrib.sessions',
                    'django_models',  # 你的模型应用
                    'rest_framework',  # Django REST Framework
                    'api',  # API 应用
                    'corsheaders',  # CORS 支持
                ],
                MIDDLEWARE=[
                    'django.middleware.security.SecurityMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件
                    'django.middleware.common.CommonMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                ],
                USE_TZ=False,
                SECRET_KEY="django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5",  # 建议改为从环境变量读取
                DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',

                # 自定义用户模型认证后端（因为 User_info 不继承自 AbstractUser）
                AUTHENTICATION_BACKENDS=[
                    'api.authentication.User_infoBackend',
                ],

                # Django REST Framework 配置
                REST_FRAMEWORK={
                    'DEFAULT_AUTHENTICATION_CLASSES': [
                        'api.authentication.SessionAuthentication',  # 使用禁用 CSRF 的自定义认证类
                    ],
                    'DEFAULT_PERMISSION_CLASSES': [
                        'rest_framework.permissions.IsAuthenticated',
                    ],
                    'DEFAULT_RENDERER_CLASSES': [
                        'rest_framework.renderers.JSONRenderer',
                    ],
                    'DEFAULT_PARSER_CLASSES': [
                        'rest_framework.parsers.JSONParser',
                        'rest_framework.parsers.MultiPartParser',
                        'rest_framework.parsers.FormParser',
                    ],
                    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
                    'PAGE_SIZE': 10,
                },

                # CORS 配置
                CORS_ALLOWED_ORIGINS=[
                    "http://localhost:24610",  # Vue 开发服务器
                    "http://127.0.0.1:24610",
                ],
                CORS_ALLOW_CREDENTIALS=True,
                CORS_ALLOW_ALL_ORIGINS=False,  # 生产环境应设为 False

                # CSRF 配置（豁免 CORS 允许的来源）
                CSRF_TRUSTED_ORIGINS=[
                    "http://localhost:24610",
                    "http://127.0.0.1:24610",
                ],
                # 对于 Session 认证，使用 session 来存储 CSRF token
                CSRF_USE_SESSIONS=True,
                CSRF_COOKIE_HTTPONLY=False,

                # Session 配置
                SESSION_COOKIE_NAME='sessionid',
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Lax',

                # 禁用系统检查（减少警告）
                # 注意：django_server.py 使用了直接启动方式，完全绕过系统检查
                SILENCED_SYSTEM_CHECKS=[
                    'django.db.backends.mysql.base',
                    'django.core.management.CheckMigration',  # 禁用迁移检查
                    'django.core.management.CheckDefaultDatabaseIsAllowed',  # 禁用数据库检查
                ],

                # URL 配置
                ROOT_URLCONF='config.urls',

                # 静态文件配置
                STATIC_URL='/static/',
                STATICFILES_DIRS=[
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
                ],

                # 发布相关配置
                PUBLISH_CONFIG={

                # 日志配置
                LOGGING={
                    'version': 1,
                    'disable_existing_loggers': False,
                    'formatters': {
                        'verbose': {
                            'format': '[{levelname}] {asctime} {module} {message}',
                            'style': '{',
                        },
                    },
                    'handlers': {
                        'console': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'verbose',
                        },
                    },
                    'root': {
                        'handlers': ['console'],
                        'level': 'INFO',
                    },
                    'loggers': {
                        'django': {
                            'handlers': ['console'],
                            'level': 'INFO',
                            'propagate': False,
                        },
                        'api': {
                            'handlers': ['console'],
                            'level': 'INFO',
                            'propagate': False,
                        },
                    },
                },

                # 发布相关配置
                PUBLISH_CONFIG={
                    'pdf_output_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/pdfs'),
                    'json_archive_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archived'),
                    'latest_json_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/latest.json'),
                    'latest_pdf_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/latest.pdf'),
                    'typst_template_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/news_template.typ'),
                    'fonts_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts'),
                    'typst_command': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'typst.exe') if os.name == 'nt' else 'typst',
                },
            )
        except Exception as e:
            logger.error(f"[Database] Failed to configure Django: {e}")
            sys.exit(1)