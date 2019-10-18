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
日志管理模块

访问日志管理
系统消息管理
"""
from flask_admin.contrib.mongoengine.filters import FilterNotEqual

from app.extensions.logger import models as logm

from .bases import AuthMongView
from ..formaters import json_formatter


class LogModelView(AuthMongView):
    """访问日志管理"""

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    column_exclude_list = ['arguments', 'url']

    column_default_sort = [('created', True)]
    column_formatters = {'arguments': json_formatter}
    column_filters = ['created', FilterNotEqual(logm.Log.module, '去除模块')]


class MsgModelView(AuthMongView):
    """系统消息管理"""

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    column_formatters = {'message': json_formatter}
    column_default_sort = [('created', True)]
    column_filters = ['created']
