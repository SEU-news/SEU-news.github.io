"""
API 视图统一导出

从这个模块可以导入所有视图类
"""

from .auth import (
    LoginAPIView,
    RegisterAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
)
from .content import (
    ContentListAPIView,
    ContentCreateAPIView,
    ContentDetailAPIView,
    ContentModifyAPIView,
    ContentSubmitAPIView,
    ContentReviewAPIView,
    ContentRecallAPIView,
    ContentCancelAPIView,
    ContentAdminStatusAPIView,
)
from .admin import (
    UserAdminListAPIView,
    UserRoleEditAPIView,
    UserEditAPIView,
    AdminDashboardAPIView,
)
from .publish import (
    PublishAPIView,
)
from .export import (
    ExportPDFAPIView,
    ExportTypstAPIView,
    ExportLatexAPIView,
    ExportDataAPIView,
)
from .utility import (
    UnifiedUploadAPIView,
    SearchAPIView,
    PreviewAPIView,
)

__all__ = [
    # Auth views
    'LoginAPIView',
    'RegisterAPIView',
    'LogoutAPIView',
    'CurrentUserAPIView',
    'ChangePasswordAPIView',
    # Content views
    'ContentListAPIView',
    'ContentCreateAPIView',
    'ContentDetailAPIView',
    'ContentModifyAPIView',  # POST: 描述(已废弃), PATCH: 更新
    'ContentSubmitAPIView',
    'ContentReviewAPIView',
    'ContentRecallAPIView',
    'ContentCancelAPIView',
    'ContentAdminStatusAPIView',
    # Admin views
    'UserAdminListAPIView',
    'UserRoleEditAPIView',
    'UserEditAPIView',
    'AdminDashboardAPIView',
    # Publish views
    'PublishAPIView',
    # Export views
    'ExportPDFAPIView',
    'ExportTypstAPIView',
    'ExportLatexAPIView',
    'ExportDataAPIView',
    # Utility views
    'UnifiedUploadAPIView',
    'SearchAPIView',
    'PreviewAPIView',
]
