import sys
from hashlib import md5
import logging
from django.conf import settings


def configure_django():
    # if not settings.configured:

    user_dict=read_credentials()
    if user_dict is None:
        logging.error("[Database] No credentials provided")
        sys.exit(1)

    user,password = list(user_dict.items())[0]

    logging.info(f"[Database] Using database credentials - User: {user}, Password MD5: {md5(password.encode('utf-8')).hexdigest()}")

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
                }
            }
        },
        INSTALLED_APPS=[
            'django_models',  # 你的模型应用
        ],
        USE_TZ=True,
        TIME_ZONE='UTC',
        SECRET_KEY="django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5",  # 用于 Django 的会话等
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

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