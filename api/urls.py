"""
API URL 配置

定义所有 API 端点的路由
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from api.views import (
    LoginAPIView,
    RegisterAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
    ContentListAPIView,
    AdminContentListAPIView,
    ContentDetailAPIView,
    ContentModifyAPIView,
    ContentReviewAPIView,
    ContentRecallAPIView,
    ContentCancelAPIView,
    ContentStatusUpdateAPIView,
    PublishAPIView,
    TypstAPIView,
    LatexAPIView,
    UnifiedUploadAPIView,
    SearchAPIView,
    PreviewAPIView,
    UserAdminListAPIView,
    UserRoleEditAPIView,
    UserEditAPIView,
    AddDeadlineAPIView,
    AdminDashboardAPIView,
)


# ==================== 认证相关 ====================
urlpatterns = [
    # 认证（豁免 CSRF）
    path('auth/login/', csrf_exempt(LoginAPIView.as_view()), name='api_login'),
    path('auth/logout/', csrf_exempt(LogoutAPIView.as_view()), name='api_logout'),
    path('auth/register/', csrf_exempt(RegisterAPIView.as_view()), name='api_register'),
    path('auth/user/', CurrentUserAPIView.as_view(), name='api_current_user'),
    path('auth/password/', csrf_exempt(ChangePasswordAPIView.as_view()), name='api_change_password'),

    # 内容管理
    path('content/', csrf_exempt(ContentListAPIView.as_view()), name='api_content_list'),  # 列表(GET) + 创建(POST) - /manage/list
    path('admin/entries/', AdminContentListAPIView.as_view(), name='api_admin_entries'),  # 管理员内容列表 - /manage/admin/entries
    path('content/<int:pk>/', ContentDetailAPIView.as_view(), name='api_content_detail'),  # 详情
    path('content/<int:pk>/modify/', csrf_exempt(ContentModifyAPIView.as_view()), name='api_content_modify'),
    path('content/<int:pk>/review/', csrf_exempt(ContentReviewAPIView.as_view()), name='api_content_review'),
    path('content/<int:pk>/recall/', csrf_exempt(ContentRecallAPIView.as_view()), name='api_content_recall'),
    path('content/<int:pk>/cancel/', csrf_exempt(ContentCancelAPIView.as_view()), name='api_content_cancel'),  # 取消
    path('content/<int:pk>/status/', csrf_exempt(ContentStatusUpdateAPIView.as_view()), name='content_status_update'),  # 状态更新

    # 文件上传（统一上传 API）
    path('upload/', csrf_exempt(UnifiedUploadAPIView.as_view()), name='api_upload'),

    # 搜索
    path('search/', csrf_exempt(SearchAPIView.as_view()), name='api_search'),

    # 预览
    path('preview/', csrf_exempt(PreviewAPIView.as_view()), name='api_preview'),  # 预览（新增）

    # 发布相关
    path('publish/', csrf_exempt(PublishAPIView.as_view()), name='api_publish'),
    path('typst/<str:date>/', TypstAPIView.as_view(), name='api_typst'),
    path('latex/<str:date>/', LatexAPIView.as_view(), name='api_latex'),

    # 用户管理
    path('admin/users/', UserAdminListAPIView.as_view(), name='api_admin_users'),
    path('admin/users/<int:user_id>/role/', csrf_exempt(UserRoleEditAPIView.as_view()), name='api_user_role_edit'),  # 角色编辑（新增）
    path('admin/users/<int:user_id>/', csrf_exempt(UserEditAPIView.as_view()), name='api_user_edit'),  # 用户编辑（新增）
    path('admin/deadlines/', csrf_exempt(AddDeadlineAPIView.as_view()), name='api_admin_deadlines'),
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='api_admin_dashboard'),  # 管理面板（新增）
]
