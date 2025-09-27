import logging

# 全局状态常量定义
STATUS_DRAFT = 'draft'
STATUS_PENDING = 'pending'
STATUS_REVIEWED = 'reviewed'
STATUS_REJECTED = 'rejected'
STATUS_PUBLISHED = 'published'
STATUS_TERMINATED = 'terminated'

_status_map: dict[str, str] = {
    STATUS_PENDING: '待审核',
    STATUS_PUBLISHED: '已发布',
    STATUS_REVIEWED: '已审核',
    STATUS_REJECTED: '已拒绝',
    STATUS_DRAFT: '草稿',
    STATUS_TERMINATED: '已终止'
}

_valid_transitions = {
    STATUS_DRAFT: [STATUS_PENDING, STATUS_TERMINATED],
    STATUS_PENDING: [STATUS_REVIEWED, STATUS_REJECTED],
    STATUS_REVIEWED: [STATUS_PUBLISHED, STATUS_PENDING],
    STATUS_REJECTED: [STATUS_PENDING],
    STATUS_PUBLISHED: [STATUS_TERMINATED],
    STATUS_TERMINATED: []
}


class ContentStatus:
    """内容状态管理类，用于处理内容的各种状态转换和显示"""

    def __init__(self, status: str) -> None:
        """
        初始化内容状态

        Args:
            status: 英文状态标识
        """
        self._logger = logging.getLogger("Content_Status")
        self._status = status
        if not self.is_valid():
            self._status = STATUS_PENDING

    def string_en(self) -> str:
        """
        获取英文状态标识
        
        Returns:
            str: 英文状态标识
        """
        return self._status

    def string_cn(self) -> str:
        """
        获取中文状态显示
        
        Returns:
            str: 中文状态显示
        """
        return _status_map.get(self._status, '待审核')

    def is_valid(self) -> bool:
        """
        验证状态是否有效

        Returns:
            bool: 状态是否有效
        """
        return self._status in _status_map

    def _can_transit_to(self, target_status: str) -> bool:
        """
        检查是否可以转换到目标状态
        
        Args:
            target_status: 目标状态
            
        Returns:
            bool: 是否可以转换
        """

        return target_status in _valid_transitions.get(self._status, [])

    def submit(self) -> bool:
        """
        draft -> pending
        提交草稿进行审核
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_PENDING):
            self._status = STATUS_PENDING
            return True
        return False

    def abandon(self) -> bool:
        """
        draft -> terminated
        放弃/删除草稿
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_TERMINATED):
            self._status = STATUS_TERMINATED
            return True
        return False

    def approve(self) -> bool:
        """
        pending -> reviewed
        审核通过
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_REVIEWED):
            self._status = STATUS_REVIEWED
            return True
        return False

    def reject(self) -> bool:
        """
        pending -> rejected
        审核不通过
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_REJECTED):
            self._status = STATUS_REJECTED
            return True
        return False

    def publish(self) -> bool:
        """
        reviewed -> published
        确认发布
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_PUBLISHED):
            self._status = STATUS_PUBLISHED
            return True
        return False

    def return_for_revision(self) -> bool:
        """
        reviewed -> pending
        返回修改
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_PENDING):
            self._status = STATUS_PENDING
            return True
        return False

    def resubmit(self) -> bool:
        """
        rejected -> pending
        重新提交
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_PENDING):
            self._status = STATUS_PENDING
            return True
        return False

    def archive(self) -> bool:
        """
        published -> terminated
        下线/归档
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to(STATUS_TERMINATED):
            self._status = STATUS_TERMINATED
            return True
        return False