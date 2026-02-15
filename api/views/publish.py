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

logger = logging.getLogger(__name__)


class PublishAPIView(APIView):
    """
    批量发布内容

    POST /api/publish/
    请求体: {"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            content_ids = request.data.get('content_ids', [])

            result = PublishService.publish_contents(request.user, content_ids)

            return Response({
                'success': True,
                'updated': result['updated'],
                'failed': result['failed']
            })
        except APIException as e:
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
