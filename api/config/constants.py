"""
常量定义
将硬编码值集中管理，便于维护和修改
"""

# ===== 内容状态 =====
CONTENT_STATUS_DRAFT = 'draft'
CONTENT_STATUS_PENDING = 'pending'
CONTENT_STATUS_REVIEWED = 'reviewed'
CONTENT_STATUS_REJECTED = 'rejected'
CONTENT_STATUS_PUBLISHED = 'published'
CONTENT_STATUS_TERMINATED = 'terminated'

CONTENT_STATUS_CHOICES = [
    (CONTENT_STATUS_DRAFT, '草稿'),
    (CONTENT_STATUS_PENDING, '待审核'),
    (CONTENT_STATUS_REVIEWED, '已审核'),
    (CONTENT_STATUS_REJECTED, '已拒绝'),
    (CONTENT_STATUS_PUBLISHED, '已发布'),
    (CONTENT_STATUS_TERMINATED, '已终止'),
]

ALLOWED_CONTENT_STATUSES = [
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_PENDING,
    CONTENT_STATUS_REVIEWED,
    CONTENT_STATUS_REJECTED,
    CONTENT_STATUS_PUBLISHED,
]

ACTIVE_CONTENT_STATUSES = [
    CONTENT_STATUS_DRAFT,
    CONTENT_STATUS_PENDING,
    CONTENT_STATUS_REVIEWED,
    CONTENT_STATUS_PUBLISHED,
]

# ===== 内容类型 =====
CONTENT_TYPES = ['教务', '竞赛', '活动', '讲座', '其他']

# ===== Typst 配置 =====
TYPST_VERSIONS = {
    'no': 1,
    'first-v': 3,
    'lecture-v': 3,
    'other-v': 3,
    'college-v': 3,
    'club-v': 3,
}

TYPST_CATEGORIES = ['college', 'club', 'lecture', 'other']

# ===== 文件上传 =====
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = 'uploads'

# ===== 分页配置 =====
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# ===== 用户权限 =====
PERMISSION_NONE = 0b00  # 0 - 无权限
PERMISSION_EDITOR = 0b01  # 1 - 编辑权限
PERMISSION_ADMIN = 0b10  # 2 - 管理员权限
PERMISSION_ALL = 0b11  # 3 - 所有权限

PERMISSION_CHOICES = [
    (PERMISSION_NONE, '普通用户'),
    (PERMISSION_EDITOR, '编辑'),
    (PERMISSION_ADMIN, '管理员'),
    (PERMISSION_ALL, '超级管理员'),
]
