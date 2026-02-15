"""
导出相关视图

包含：PDF 生成、Typst 生成、LaTeX 生成、导出数据获取
"""

import logging
from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsEditorOrAdmin
from api.services.export_service import ExportService
from api.core.exceptions import APIException

logger = logging.getLogger(__name__)


class ExportPDFAPIView(APIView):
    """
    生成 PDF 文件

    POST /api/v1/export/pdf/
    请求体: {"date": "2026-02-11"} 或 {"content_ids": [1, 2, 3]}

    支持两种模式：
    1. 按日期生成：{"date": "2026-02-11"}
    2. 按选中内容生成：{"content_ids": [1, 2, 3]}
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    @method_decorator(csrf_exempt)
    def post(self, request):
        """生成 PDF 文件"""
        try:
            date_str = request.data.get('date')
            content_ids = request.data.get('content_ids')

            # 验证参数：至少提供 date 或 content_ids
            if not date_str and not content_ids:
                return Response(
                    {'success': False, 'message': '请提供 date 或 content_ids 参数'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 如果提供了 date，验证日期格式
            if date_str:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    return Response(
                        {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 调用导出服务
            result = ExportService.generate_pdf(date_str=date_str, content_ids=content_ids)

            if not result['success']:
                return Response(
                    {'success': False, 'message': result['message']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'success': True,
                'message': 'PDF 生成成功',
                'pdf_url': result['pdf_url'],
                'pdf_path': result['pdf_path'],
                'count': result.get('count', 0),
                'due_contents': result.get('due_contents', {})
            })
        except APIException as e:
            logger.error(f"PDF 生成失败: {e.message}")
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
        except Exception as e:
            logger.error(f"PDF 生成过程中发生异常: {e}")
            return Response(
                {'success': False, 'message': f'PDF 生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportTypstAPIView(APIView):
    """
    生成 Typst 格式文档

    GET /api/v1/export/typst/?date=2026-02-11
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        """返回 Typst 数据"""
        try:
            date = request.query_params.get('date')
            if not date:
                return Response(
                    {'success': False, 'message': '请提供 date 参数'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证日期格式
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            typst_data = ExportService.generate_typst(date)

            return Response({
                'success': True,
                'date': date,
                'data': typst_data
            })
        except APIException as e:
            logger.error(f"Typst 数据生成失败: {e.message}")
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
        except Exception as e:
            logger.error(f"Typst 数据生成过程中发生异常: {e}")
            return Response(
                {'success': False, 'message': f'Typst 数据生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportLatexAPIView(APIView):
    """
    生成 LaTeX 格式文档

    GET /api/v1/export/latex/?date=2026-02-11
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        """返回 LaTeX 数据"""
        try:
            date = request.query_params.get('date')
            if not date:
                return Response(
                    {'success': False, 'message': '请提供 date 参数'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证日期格式
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            latex_data = ExportService.generate_latex(date)

            return Response({
                'success': True,
                'date': date,
                'data': latex_data
            })
        except APIException as e:
            logger.error(f"LaTeX 数据生成失败: {e.message}")
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
        except Exception as e:
            logger.error(f"LaTeX 数据生成过程中发生异常: {e}")
            return Response(
                {'success': False, 'message': f'LaTeX 数据生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportDataAPIView(APIView):
    """
    获取导出数据（Flask 兼容格式）

    GET /api/v1/export/data/?date=2026-02-11
    """
    permission_classes = [IsAuthenticated, IsEditorOrAdmin]

    def get(self, request):
        """返回 Flask 兼容的导出数据"""
        try:
            date = request.query_params.get('date')
            if not date:
                return Response(
                    {'success': False, 'message': '请提供 date 参数'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证日期格式
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'success': False, 'message': '日期格式无效，请使用 YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            export_data = ExportService.get_export_data(date)

            return Response({
                'success': True,
                'date': date,
                'data': export_data
            })
        except APIException as e:
            logger.error(f"导出数据获取失败: {e.message}")
            return Response(
                {'success': False, 'message': e.message},
                status=e.status
            )
        except Exception as e:
            logger.error(f"导出数据获取过程中发生异常: {e}")
            return Response(
                {'success': False, 'message': f'导出数据获取失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
