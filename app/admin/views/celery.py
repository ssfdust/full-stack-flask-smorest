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
celery的管理模块

调度任务管理
任务状态管理
"""

from ..formaters import json_formatter, line_formatter
from .bases import AuthMongView
from ..forms import TaskSelect2Field


class CeleryScheduleView(AuthMongView):
    """
    调度任务管理

    用以创建调度任务，支持两种格式一是Crontab，
    二是Interval，两种方式只能选择一种。
    """
    from app.extensions.mongobeat.models import PeriodicTask

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    extra_js = ['/static/js/pages/celerybeat.js']  # 拓展表单的js
    column_list = ['name', 'task', 'enabled', 'schedule', 'last_run_at']
    column_labels = {'schedule': '周期'}
    column_editable_list = ['enabled', 'run_immediately']
    column_default_sort = []
    column_filters = ['name']
    can_view_details = True
    form_overrides = {
        'task': TaskSelect2Field
    }

    def _scheduleinfo(view, context, model, name):
        """调度信息展示"""
        return str(model).split(':')[1]

    column_formatters = {
        'schedule': _scheduleinfo
    }


class CeleryTaskView(AuthMongView):
    """任务查看"""

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    details_modal = False
    column_default_sort = [('time_start', True)]
    column_filters = ['time_start', 'date_done']
    column_exclude_list = ['id', 'delivery_info', 'result', 'children', 'args',
                           'acknowledged', 'traceback', 'kwargs', 'parent_id',
                           'type']
    column_formatters = {'delivery_info': json_formatter,
                         'result': json_formatter,
                         'traceback': line_formatter
                         }

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        """将所有任务置为已读"""
        count, query = super().get_list(page=page, sort_column=sort_column,
                                        sort_desc=sort_desc,
                                        search=search, filters=filters,
                                        execute=execute, page_size=page_size)
        for item in query:
            if item.checked is False:
                item.checked = True
                item.save()

        return count, query
