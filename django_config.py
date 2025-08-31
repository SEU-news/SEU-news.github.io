from django.conf import settings


def configure_django():
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
                'django_models',  # 你的模型应用
            ],
            USE_TZ=True,
            TIME_ZONE='UTC',
            SECRET_KEY="django-insecure-8!563mqn=(m8$hryw5_1!j!eb*^i^lidx^v2xh6+@+i@$r@4o5",  # 用于 Django 的会话等
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )