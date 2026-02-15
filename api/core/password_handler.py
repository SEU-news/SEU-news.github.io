"""
密码处理器
封装密码哈希和验证逻辑（保持与现有系统兼容）
"""

import hashlib


class PasswordHandler:
    """密码处理器"""

    ALGORITHM = 'md5'  # 保持 MD5（与现有系统兼容）

    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码

        Args:
            password: 明文密码

        Returns:
            MD5 哈希后的密码字符串
        """
        if not password:
            raise ValueError("Password cannot be empty")
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            hashed: 哈希后的密码

        Returns:
            密码是否匹配
        """
        if not password or not hashed:
            return False
        input_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        return input_hash == hashed

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        验证密码强度

        Args:
            password: 待验证的密码

        Returns:
            (是否通过, 错误消息)
        """
        from api.config.constants import PERMISSION_NONE

        if len(password) < 6:
            return False, "密码长度至少为 6 位"

        return True, ""
