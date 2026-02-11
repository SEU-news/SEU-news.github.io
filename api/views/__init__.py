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
    AdminContentListAPIView,
    ContentDetailAPIView,
    ContentDescribeAPIView,
    ContentReviewAPIView,
    ContentRecallAPIView,
    ContentCancelAPIView,
    ContentStatusUpdateAPIView,
)
from .admin import (
    UserAdminListAPIView,
    UserRoleEditAPIView,
    UserEditAPIView,
    AddDeadlineAPIView,
    AdminDashboardAPIView,
)
from .publish import (
    PublishAPIView,
    PublishDataAPIView,
    GeneratePDFAPIView,
    GeneratePDFFromSelectionAPIView,
    QueryPublishedByDateAPIView,
    QueryDDLByDateAPIView,
    UnpublishAPIView,
    TypstAPIView,
    LatexAPIView,
)
from .utility import (
    UnifiedUploadAPIView,
    SearchAPIView,
    PreviewAPIView,
)

# ContentModifyAPIView 是 ContentDescribeAPIView 的别名
# 用于保持与原始路由的兼容性
ContentModifyAPIView = ContentDescribeAPIView

__all__ = [
    # Auth views
    'LoginAPIView',
    'RegisterAPIView',
    'LogoutAPIView',
    'CurrentUserAPIView',
    'ChangePasswordAPIView',
    # Content views
    'ContentListAPIView',
    'AdminContentListAPIView',
    'ContentDetailAPIView',
    'ContentDescribeAPIView',
    'ContentModifyAPIView',  # Alias for ContentDescribeAPIView
    'ContentReviewAPIView',
    'ContentRecallAPIView',
    'ContentCancelAPIView',
    'ContentStatusUpdateAPIView',
    # Admin views
    'UserAdminListAPIView',
    'UserRoleEditAPIView',
    'UserEditAPIView',
    'AddDeadlineAPIView',
    'AdminDashboardAPIView',
    # Publish views
    'PublishAPIView',
    'PublishDataAPIView',
    'GeneratePDFAPIView',
    'GeneratePDFFromSelectionAPIView',
    'QueryPublishedByDateAPIView',
    'QueryDDLByDateAPIView',
    'UnpublishAPIView',
    'TypstAPIView',
    'LatexAPIView',
    # Utility views
    'UnifiedUploadAPIView',
    'SearchAPIView',
    'PreviewAPIView',
]
