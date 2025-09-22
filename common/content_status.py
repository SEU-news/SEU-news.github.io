import logging

_status_map: dict[str, str] = {
    'pending': '待审核',
    'published': '已发布',
    'reviewed': '已审核',
    'rejected': '已拒绝',
    'draft': '草稿',
    'terminated': '已终止'
}

_valid_transitions = {
    'draft': ['pending', 'terminated'],
    'pending': ['reviewed', 'rejected'],
    'reviewed': ['published', 'pending'],
    'rejected': ['pending'],
    'published': ['terminated'],
    'terminated': []
}


class ContentStatus:
    """内容状态管理类，用于处理内容的各种状态转换和显示"""

    def __init__(self, status: str) -> None:
        """
        初始化内容状态

        Args:
            status: 英文状态标识
        """
        self.logger = logging.getLogger("Content_Status")
        self.status = status
        if not self.is_valid():
            self.status = 'pending'

    def get_status_display_en(self) -> str:
        """
        获取英文状态标识
        
        Returns:
            str: 英文状态标识
        """
        return self.status

    def get_status_display_cn(self) -> str:
        """
        获取中文状态显示
        
        Returns:
            str: 中文状态显示
        """
        return _status_map.get(self.status, '待审核')

    def is_valid(self) -> bool:
        """
        验证状态是否有效

        Returns:
            bool: 状态是否有效
        """
        return self.status in _status_map

    def _can_transit_to(self, target_status: str) -> bool:
        """
        检查是否可以转换到目标状态
        
        Args:
            target_status: 目标状态
            
        Returns:
            bool: 是否可以转换
        """

        return target_status in _valid_transitions.get(self.status, [])

    def submit(self) -> bool:
        """
        draft -> pending
        提交草稿进行审核
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('pending'):
            self.status = 'pending'
            return True
        return False

    def abandon(self) -> bool:
        """
        draft -> terminated
        放弃/删除草稿
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('terminated'):
            self.status = 'terminated'
            return True
        return False

    def approve(self) -> bool:
        """
        pending -> reviewed
        审核通过
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('reviewed'):
            self.status = 'reviewed'
            return True
        return False

    def reject(self) -> bool:
        """
        pending -> rejected
        审核不通过
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('rejected'):
            self.status = 'rejected'
            return True
        return False

    def publish(self) -> bool:
        """
        reviewed -> published
        确认发布
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('published'):
            self.status = 'published'
            return True
        return False

    def return_for_revision(self) -> bool:
        """
        reviewed -> pending
        返回修改
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('pending'):
            self.status = 'pending'
            return True
        return False

    def resubmit(self) -> bool:
        """
        rejected -> pending
        重新提交
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('pending'):
            self.status = 'pending'
            return True
        return False

    def archive(self) -> bool:
        """
        published -> terminated
        下线/归档
        
        Returns:
            bool: 转换是否成功
        """
        if self._can_transit_to('terminated'):
            self.status = 'terminated'
            return True
        return False
