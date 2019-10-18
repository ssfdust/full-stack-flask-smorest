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
    app.modules.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~

    用户、权限、组相关模块
"""

from flask_smorest import Blueprint

from app.extensions import api

from . import permissions

ROLES = permissions.ROLES  # alias

PERMISSIONS = permissions.PERMISSIONS  # alias

blp = Blueprint(
    'Auth', __name__, url_prefix='/auth',
    description='用户登录退出密码管理模块'
)


def init_app(app):
    """初始化模块

    :param app: Flask Flask实例
    """
    from .import views, models  # noqa

    base_prefix = app.config['MODULE_BASE_PREFIX'] if 'MODULE_BASE_PREFIX' in app.config else ''

    api.register_blueprint(blp, base_prefix=base_prefix)

