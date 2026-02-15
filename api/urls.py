"""
API URL 配置

定义所有 API 端点的路由

RESTful 设计说明：
- CRUD 操作使用标准 REST 方法（GET/POST/PUT/PATCH/DELETE）
- 特殊操作使用 POST 到资源子路径（如 /modify/, /review/, /recall/, /cancel/）
- 文件上传统一到 /upload/ 端点，通过 upload_type 参数区分类型（text/url/image）
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
    ContentCreateAPIView,
    ContentDetailAPIView,
    ContentModifyAPIView,
    ContentSubmitAPIView,
    ContentReviewAPIView,
    ContentRecallAPIView,
    ContentCancelAPIView,
    ContentAdminStatusAPIView,
    PublishAPIView,
    UnifiedUploadAPIView,
    SearchAPIView,
    PreviewAPIView,
    UserAdminListAPIView,
    UserRoleEditAPIView,
    UserEditAPIView,
    AdminDashboardAPIView,
)
from api.views.export import (
    ExportPDFAPIView,
    ExportTypstAPIView,
    ExportLatexAPIView,
    ExportDataAPIView,
)


# ==================== 认证相关 ====================
urlpatterns = [
    # 认证（豁免 CSRF）
    path('auth/login/', csrf_exempt(LoginAPIView.as_view()), name='api_login'),
    path('auth/logout/', csrf_exempt(LogoutAPIView.as_view()), name='api_logout'),
    path('auth/register/', csrf_exempt(RegisterAPIView.as_view()), name='api_register'),
    path('auth/user/', CurrentUserAPIView.as_view(), name='api_current_user'),
    path('auth/password/', csrf_exempt(ChangePasswordAPIView.as_view()), name='api_change_password'),

    # ==================== 内容管理 ====================
    # 内容列表：GET /api/contents/ - 获取内容列表（复数形式）
    # 内容创建：POST /api/content/create/ - 创建内容
    # 内容详情/更新：GET /api/content/<id>/ - 详情, PATCH /api/content/<id>/modify/ - 更新
    # 内容状态操作：提交审核、审核、撤回、取消
    path('contents/', ContentListAPIView.as_view(), name='api_content_list'),  # 列表 - 所有用户
    path('content/create/', csrf_exempt(ContentCreateAPIView.as_view()), name='api_content_create'),  # 创建(POST)
    path('content/<int:pk>/', ContentDetailAPIView.as_view(), name='api_content_detail'),  # 详情
    path('content/<int:pk>/modify/', csrf_exempt(ContentModifyAPIView.as_view()), name='api_content_modify'),  # 更新(PATCH)
    path('content/<int:pk>/submit/', csrf_exempt(ContentSubmitAPIView.as_view()), name='api_content_submit'),  # 提交审核
    path('content/<int:pk>/review/', csrf_exempt(ContentReviewAPIView.as_view()), name='api_content_review'),
    path('content/<int:pk>/recall/', csrf_exempt(ContentRecallAPIView.as_view()), name='api_content_recall'),
    path('content/<int:pk>/cancel/', csrf_exempt(ContentCancelAPIView.as_view()), name='api_content_cancel'),  # 取消
    path('content/<int:pk>/admin_status/', csrf_exempt(ContentAdminStatusAPIView.as_view()), name='api_content_admin_status'),  # 管理员强制修改状态

    # 文件上传（统一上传 API）
    path('upload/', csrf_exempt(UnifiedUploadAPIView.as_view()), name='api_upload'),

    # 搜索
    path('search/', csrf_exempt(SearchAPIView.as_view()), name='api_search'),

    # 预览
    path('preview/', csrf_exempt(PreviewAPIView.as_view()), name='api_preview'),  # 预览（新增）

    # 发布相关
    path('publish/', csrf_exempt(PublishAPIView.as_view()), name='api_publish'),

    # 文档导出（v1 版本）
    path('v1/export/pdf/', csrf_exempt(ExportPDFAPIView.as_view()), name='api_export_pdf'),
    path('v1/export/typst/', ExportTypstAPIView.as_view(), name='api_export_typst'),
    path('v1/export/latex/', ExportLatexAPIView.as_view(), name='api_export_latex'),
    path('v1/export/data/', ExportDataAPIView.as_view(), name='api_export_data'),

    # 用户管理
    path('admin/users/', UserAdminListAPIView.as_view(), name='api_admin_users'),
    path('admin/users/<int:user_id>/role/', csrf_exempt(UserRoleEditAPIView.as_view()), name='api_user_role_edit'),  # 角色编辑（新增）
    path('admin/users/<int:user_id>/info/', csrf_exempt(UserEditAPIView.as_view()), name='api_user_info_edit'),  # 用户信息编辑（新增）
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='api_admin_dashboard'),  # 管理面板（新增）
    path('admin/users/<int:user_id>/', csrf_exempt(UserEditAPIView.as_view()), name='api_user_edit'),  # 用户编辑（新增）
]
