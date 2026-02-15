"""
自定义异常类
提供统一的异常处理接口
"""


class APIException(Exception):
    """API 基础异常"""

    def __init__(self, message: str, code: str = 'error', status: int = 400):
        """
        Args:
            message: 错误消息
            code: 错误代码
            status: HTTP 状态码
        """
        self.message = message
        self.code = code
        self.status = status
        super().__init__(message)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'code': self.code,
            'message': self.message,
        }


class ValidationError(APIException):
    """数据验证错误 (400)"""

    def __init__(self, message: str):
        super().__init__(message, code='validation_error', status=400)


class AuthenticationError(APIException):
    """认证错误 (401)"""

    def __init__(self, message: str = 'Authentication required'):
        super().__init__(message, code='authentication_error', status=401)


class PermissionDeniedError(APIException):
    """权限错误 (403)"""

    def __init__(self, message: str = 'Permission denied'):
        super().__init__(message, code='permission_denied', status=403)


class NotFoundError(APIException):
    """资源不存在 (404)"""

    def __init__(self, message: str = 'Resource not found'):
        super().__init__(message, code='not_found', status=404)


class BusinessLogicError(APIException):
    """业务逻辑错误 (422)"""

    def __init__(self, message: str):
        super().__init__(message, code='business_logic_error', status=422)


class ConflictError(APIException):
    """冲突错误 (409)"""

    def __init__(self, message: str):
        super().__init__(message, code='conflict', status=409)
