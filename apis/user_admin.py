import logging

from flask import session, render_template, request
from flask.views import MethodView

from common.decorator.permission_required import PermissionDecorators
from django_models.models import Content, User_info

class UserAdminView(MethodView):

    decorators = [PermissionDecorators.admin_required]# 应用装饰器到整个视图类
def user_admin(self):
    """空的用户管理方法"""
    pass