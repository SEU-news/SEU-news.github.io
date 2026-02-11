"""
主 URL 配置

将 API 路由挂载到 /api/ 前缀
"""

from django.urls import path, include

urlpatterns = [
    path('api/', include('api.urls')),
]
