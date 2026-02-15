"""
应用配置类
集中管理应用级别的配置参数
"""


class AppConfig:
    """应用配置类"""

    # ===== 密码策略 =====
    PASSWORD_MIN_LENGTH = 6  # 最小密码长度（与现有系统保持一致）
    PASSWORD_MAX_LENGTH = 100

    # ===== 搜索配置 =====
    SEARCH_MIN_LENGTH = 1
    SEARCH_MAX_RESULTS = 100

    # ===== 会话配置 =====
    SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 天

    # ===== API 配置 =====
    API_DEFAULT_PAGE_SIZE = 10
    API_MAX_PAGE_SIZE = 100

    # ===== 内容状态流转规则 =====
    # 定义允许的状态转换
    STATUS_TRANSITIONS = {
        'draft': ['pending', 'terminated'],
        'pending': ['reviewed', 'rejected', 'draft'],
        'reviewed': ['published', 'rejected'],
        'rejected': ['draft'],
        'published': ['draft'],  # 已发布可以撤回
        'terminated': [],  # 终止状态不可转换
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """检查状态转换是否允许"""
        allowed_transitions = cls.STATUS_TRANSITIONS.get(from_status, [])
        return to_status in allowed_transitions


# 全局配置实例
app_config = AppConfig()
