#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 RedLotus <ssfdust@gmail.com>
# Author: RedLotus <ssfdust@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    app.modules.auth.decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    系统的权限装饰器模块

    为请求添加权限装饰器，参数为权限
"""

from functools import wraps
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, current_user
from loguru import logger
from flask_smorest import abort

# 源码来自
# https://github.com/Nobatek/flask-rest-api/issues/36#issuecomment-460826257


def doc_login_required(func):
    '''
    登录限制装饰器

    为API添加登录限制，同时添加OpenAPI注释，使用装饰器后
    只有带有合法jwt token的请求才能访问。

    用法：
    >>> class SampleView(MethodView):
            @doc_login_required
            def get(self):
                return {'code': 0}
    '''
    # 获取登录函数
    auth_required_func = jwt_required(func)

    # 封装函数
    @wraps(func)
    def wrapper(*args, **kwargs):
        return auth_required_func(*args, **kwargs)

    # 增加验证
    wrapper._apidoc = getattr(func, '_apidoc', {})
    wrapper._apidoc.setdefault('security', [{'api_key': []}])

    return wrapper


def doc_refresh_required(func):
    '''
    刷新Token限制装饰器

    Refresh Token:
    在Jwt架构中，除了登录用的token，还有刷新token用的token。

    为API添加刷新限制，同时添加OpenAPI注释，使用装饰器后
    只有带有合法refresh token的请求才能访问。

    用法：
    >>> class SampleView(MethodView):
            @doc_refresh_required
            def get(self):
                return {'code': 0}
    '''

    # 获取刷新函数
    refresh_required_func = jwt_refresh_token_required(func)

    # 封装刷新函数
    @wraps(func)
    def wrapper(*args, **kwargs):
        return refresh_required_func(*args, **kwargs)

    # 增加swagger信息
    wrapper._apidoc = getattr(func, '_apidoc', {})
    # 设置刷新key
    wrapper._apidoc.setdefault('security', [{'refresh_key': []}])

    return wrapper


def permission_required(*permissions):
    """
    权限验证

    :param permissions: tuple 权限列

    为API添加权限限制，同时添加OpenAPI注释，使用装饰器后
    只有带有才能访问。必须在doc_login_required装饰器后。

    用法：
    >>> class SampleView(MethodView):
            @doc_login_required
            @permission_required('Permission')
            def get(self):
                return {'code': 0}
    """

    permissions = list(permissions)

    def wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            if all(permission in [p.name
                                  for p in current_user.permissions]
                   for permission in permissions):
                return func(*args, **kwargs)
            #  if all(permission in current_user.permissions
            #         for permission in permissions):
            #      return func(*args, **kwargs)
            logger.error(f"{current_user.email}不具备{permissions}")
            abort(403, message="禁止访问")

        return inner

    return wrapper


#  def role_required(*roles):
#      """
#      角色验证
#
#      :param roles: tuple 角色列
#
#      为API添加角色限制，同时添加OpenAPI注释，使用装饰器后
#      只有带有才能访问。必须在doc_login_required装饰器后。
#
#      用法：
#      >>> class SampleView(MethodView):
#              @doc_login_required
#              @role_required('Role')
#              def get(self):
#                  return {'code': 0}
#      """
#      def wrapper(func):
#
#          @wraps(func)
#          def inner(*args, **kwargs):
#              if all(role in [p.name
#                              for p in current_user.roles]
#                     for role in roles):
#                  return func(*args, **kwargs)
#              if all(role in current_user.roles for role in roles):
#                  return func(*args, **kwargs)
#              logger.error(f"{current_user.email}不具备{roles}")
#              abort(403, message="禁止访问")
#
#          return inner
#
#      return wrapper
