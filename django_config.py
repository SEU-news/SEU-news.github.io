import logging
import sys

from django.conf import settings


def configure_django():
    """
    配置Django运行环境和数据库连接参数

    该函数读取数据库凭证信息并配置Django的数据库连接，包括MySQL连接参数、
    时区设置、安全密钥等必要配置项，使Django能够在独立环境中运行。

    参数:
        无

    返回值:
        无

    异常:
        当无法读取数据库凭证时，程序将记录错误日志并退出
    """
    if not settings.configured:
        try:
            # 读取数据库用户凭证信息
            user_dict = read_credentials()
            if not user_dict or not isinstance(user_dict, dict):
                logging.error("[Database] No valid credentials provided")
                sys.exit(1)

            # 获取第一个用户凭证
            user, password = next(iter(user_dict.items()))

            # 不要记录密码！仅记录用户名用于调试
            logging.info(f"[Database] Using database credentials - User: {user}")

            # 配置Django设置，包括数据库连接、已安装应用和基本配置
            settings.configure(
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "seu_news",
                        'USER': user,
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
                USE_TZ=True,
                TIME_ZONE='UTC',
                SECRET_KEY="django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5",  # 建议改为从环境变量读取
                DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
            )
        except Exception as e:
            logging.error(f"[Configure Django] Failed to configure Django: {e}")
            sys.exit(1)


def read_credentials(file_path="credentials.txt", delimiter=':'):
    """
    从文本文件中读取账户名和密码对。

    参数:
        file_path (str): 凭证文件的路径。
        delimiter (str): 用于分隔用户名和密码的分隔符，默认为冒号（:）。

    返回:
        dict: 一个字典，键是用户名，值是对应的密码。
    """
    credentials = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()  # 去除行首尾的空白字符（包括换行符）
                if line:  # 确保不是空行
                    parts = line.split(delimiter)
                    if len(parts) == 2:
                        username, password = parts
                        credentials[username] = password
                    else:
                        logging.warn(f"警告: 跳过格式无效的行: {line}")
    except FileNotFoundError:
        logging.error(f"错误: 文件未找到 '{file_path}'")
    except Exception as e:
        logging.error(f"读取文件时发生错误: {e}")
    return credentials
