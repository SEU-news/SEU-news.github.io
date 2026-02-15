"""
django_models package
包含数据库模型定义和自定义管理器
"""

# Lazy import to avoid circular dependency
# from .models import User_info, Content, Comment
# from .managers import ContentManager, UserManager, CommentManager

__all__ = ['User_info', 'Content', 'Comment', 'ContentManager', 'UserManager', 'CommentManager']

__version__ = '1.0.0'

