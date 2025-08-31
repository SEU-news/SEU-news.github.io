#!/usr/bin/env python
"""Django management tool for Flask-Django integration"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Django 配置
if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": "mydatabase",
                'USER': 'root',
                'PASSWORD': '570455053',
                'HOST': 'localhost',  # 或者 '127.0.0.1'
                'PORT': '3306',  # 默认 MySQL 端口
                'OPTIONS': {
                    'charset': 'utf8mb4',
                }
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django_models',
        ],
        USE_TZ=True,
        SECRET_KEY='django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5',
        LANGUAGE_CODE='zh-hans',
        TIME_ZONE='Asia/Shanghai',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

    django.setup()

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
