"""
API URL 配置

定义所有 API 端点的路由
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from api import views


# ==================== 认证相关 ====================
urlpatterns = [
    # 认证（豁免 CSRF）
    path('auth/login/', csrf_exempt(views.LoginAPIView.as_view()), name='api_login'),
    path('auth/logout/', csrf_exempt(views.LogoutAPIView.as_view()), name='api_logout'),
    path('auth/register/', csrf_exempt(views.RegisterAPIView.as_view()), name='api_register'),
    path('auth/user/', views.CurrentUserAPIView.as_view(), name='api_current_user'),
    path('auth/password/', csrf_exempt(views.ChangePasswordAPIView.as_view()), name='api_change_password'),

    # 内容管理
    path('content/', csrf_exempt(views.ContentListAPIView.as_view()), name='api_content_list'),  # 列表(GET) + 创建(POST)
    path('content/<int:pk>/', views.ContentDetailAPIView.as_view(), name='api_content_detail'),  # 详情
    path('content/<int:pk>/describe/', csrf_exempt(views.ContentDescribeAPIView.as_view()), name='api_content_describe'),
    path('content/<int:pk>/review/', csrf_exempt(views.ContentReviewAPIView.as_view()), name='api_content_review'),
    path('content/<int:pk>/recall/', csrf_exempt(views.ContentRecallAPIView.as_view()), name='api_content_recall'),
    path('content/<int:pk>/cancel/', csrf_exempt(views.ContentCancelAPIView.as_view()), name='api_content_cancel'),  # 取消
    path('content/<int:pk>/status/', csrf_exempt(views.ContentStatusUpdateAPIView.as_view()), name='content_status_update'),  # 状态更新

    # 文件上传
    path('upload_image/', csrf_exempt(views.UploadImageAPIView.as_view()), name='api_upload_image'),
    path('paste/', csrf_exempt(views.PasteAPIView.as_view()), name='api_paste'),

    # 搜索
    path('search/', csrf_exempt(views.SearchAPIView.as_view()), name='api_search'),

    # 预览
    path('preview/', csrf_exempt(views.PreviewAPIView.as_view()), name='api_preview'),  # 预览（新增）

    # 发布相关
    path('publish/', csrf_exempt(views.PublishAPIView.as_view()), name='api_publish'),
    path('typst/<str:date>/', views.TypstAPIView.as_view(), name='api_typst'),
    path('latex/<str:date>/', views.LatexAPIView.as_view(), name='api_latex'),

    # 用户管理
    path('admin/users/', views.UserAdminListAPIView.as_view(), name='api_admin_users'),
    path('admin/users/<int:user_id>/role/', csrf_exempt(views.UserRoleEditAPIView.as_view()), name='api_user_role_edit'),  # 角色编辑（新增）
    path('admin/users/<int:user_id>/', csrf_exempt(views.UserEditAPIView.as_view()), name='api_user_edit'),  # 用户编辑（新增）
    path('admin/deadlines/', csrf_exempt(views.AddDeadlineAPIView.as_view()), name='api_admin_deadlines'),
    path('admin/dashboard/', views.AdminDashboardAPIView.as_view(), name='api_admin_dashboard'),  # 管理面板（新增）
]
