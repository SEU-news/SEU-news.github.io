"""
发布相关视图

包含：批量发布内容
"""

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsEditorOrAdmin
from api.services.publish_service import PublishService
from api.core.exceptions import APIException
from api.logging import get_logger

logger = get_logger(__name__)


class PublishAPIView(APIView):
    """
    批量发布内容

    POST /api/publish/
    请求体: {"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    @method_decorator(csrf_exempt)
    def post(self, request):
        # 记录请求日志
        user_info = f"user={request.user.username}, user_id={request.user.id}" if request.user.is_authenticated else "user=anonymous"
        content_ids = request.data.get('content_ids', [])
        logger.info(
            f"批量发布请求, {user_info}, content_ids={content_ids}, "
            f"count={len(content_ids)}, remote_addr={request.META.get('REMOTE_ADDR', 'N/A')}"
        )

        try:
            content_ids = request.data.get('content_ids', [])

            result = PublishService.publish_contents(request.user, content_ids)

            # 记录成功响应
            logger.info(
                f"批量发布成功, {user_info}, updated={result['updated']}, "
                f"failed={len(result['failed'])}"
            )

            return Response({
                'success': True,
                'updated': result['updated'],
                'failed': result['failed']
            })
        except APIException as e:
            # 记录 API 异常
            logger.warning(
                f"批量发布失败（业务异常）, {user_info}, content_ids={content_ids}, "
                f"error={e.message}, status={e.status}",
                exc_info=True
            )
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
        except Exception as e:
            # 记录其他异常
            logger.error(
                f"批量发布失败（系统异常）, {user_info}, content_ids={content_ids}, "
                f"error_type={type(e).__name__}, error_message={str(e)}",
                exc_info=True
            )
            raise
