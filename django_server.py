"""
Django API 开发服务器

运行 Django REST API 开发服务器（端口 42611）
"""

import os
import sys
import django

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 禁用 Django 迁移警告
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.conf')
os.environ['DJANGO_NO_MIGRATIONS'] = '1'

# 初始化统一日志系统（在 Django 配置之前）
from api.logging import setup_logging
setup_logging(
    log_dir='logs',
    log_level='DEBUG',
    console_level='INFO',
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=30,
)

# 配置 Django
from config.django_config import configure_django

try:
    configure_django()
    django.setup()
except Exception as e:
    print(f"[Error] Django 初始化失败: {e}")
    sys.exit(1)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Django REST API 开发服务器')
    parser.add_argument(
        '--port',
        type=int,
        default=42611,
        help='服务器端口（默认: 42611）'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='服务器地址（默认: 127.0.0.1）'
    )

    args = parser.parse_args()

    print("=" * 63)
    print("  SEU News Django REST API")
    print("=" * 63)
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  API Base URL: http://{args.host}:{args.port}/api/")
    print("=" * 63)
    print()

    # 使用标准的 manage.py runserver 命令
    # 虽然会有迁移警告，但服务器可以正常工作
    from django.core.management import execute_from_command_line
    
    print("启动 Django REST API...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"API Base URL: http://{args.host}:{args.port}/api/")
    print()
    
    # 标准方式启动
    execute_from_command_line(['manage.py', 'runserver', f'{args.host}:{args.port}'])
