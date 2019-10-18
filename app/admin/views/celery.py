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
from flask_admin.contrib.mongoengine.subdoc import EmbeddedForm
from flask_admin.form.fields import Select2Field

from .bases import AuthMongView
from ..formaters import json_formatter, line_formatter

class CeleryScheduleView(AuthMongView):
    """
    调度任务管理

    用以创建调度任务，支持两种格式一是Crontab，
    二是Interval，两种方式只能选择一种。
    """

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    extra_js = ['/static/js/pages/celerybeat.js']  # 拓展表单的js
    column_exclude_list = ['_cls', 'soft_time_limit', 'exchange',
                           'routing_key', 'args', 'kwargs', 'max_run_count',
                           'start_after', 'queue', 'description', 'expires',
                           'date_changed']
    form_excluded_columns = ['enabled', 'run_immediately', 'max_run_count',
                             'start_after', 'soft_time_limit', '_cls',
                             'exchange', 'last_run_at', 'total_run_count',
                             'date_changed', 'routing_key', 'expires', 'queue']
    column_editable_list = ['enabled', 'run_immediately']
    column_default_sort = []
    column_filters = ['name']
    can_view_details = True
    form_choices = {
        'type': [
            ('interval', 'interval'),
            ('crontab', 'crontab')
        ]
    }
    form_extra_fields = {
        'type': Select2Field('类型', choices=[
            ('interval', 'interval'),
            ('crontab', 'crontab'),
        ]
        )
    }
    form_create_rules = ('name', 'task', 'args',
                         'kwargs', 'description', 'type',
                         'interval', 'crontab')
    form_edit_rules = form_create_rules

    # 子栏目的表单格式化
    form_subdocuments = {
        'crontab': EmbeddedForm(form_args={
            'hour': {'label': '小时', 'validators': []},
            'minute': {'label': '分钟', 'validators': []},
            'day_of_week': {'label': '星期', 'validators': []},
            'day_of_month': {'label': '日', 'validators': []},
            'month_of_year': {'label': '月', 'validators': []}
        }),
        'interval': EmbeddedForm(form_args={
            'every': {'label': '阶段', 'validators': []},
            'period': {'label': '周期', 'validators': []}
        })
    }

    @property
    def form_args(self):
        """设置表单参数"""
        return {
            'name': {'label': '定时名称'},
            'task': {'label': '任务名称'},
            'interval': {'label': '定时'},
            'crontab': {'label': 'crontab'},
            'args': {'label': '参数'},
            'kwargs': {'label': 'kwargs'},
            'queue': {'label': '队列'},
            'no_changes': {'label': 'nochanges'},
            'exchange': {'label': 'exchange'},
            'routing_key': {'label': 'routing_key'},
            'expires': {'label': '逾期'},
            'enabled': {'label': '启用'},
            'last_run_at': {'label': '最后运行时间'},
            'total_run_count': {'label': '总计运行次数'},
            'date_changed': {'label': '改变日期'},
            'description': {'label': '描述'},
            'run_immediately': {'label': '立刻运行'},
        }

    @property
    def column_labels(self):
        """设置栏目参数"""
        labels = {
            k: v['label']
            for k, v in self.form_args.items()
        }
        labels['schedule'] = '周期'
        return labels

    def get_column_names(self, only_columns, excluded_columns):
        """新增周期栏目"""
        only_columns.append('schedule')
        return super().get_column_names(only_columns, excluded_columns)

    def on_model_change(self, form, model, is_created):
        """当设置完状态后，需要根据表单内容清空另一个表单内容"""
        if 'type' in form:
            schedule_type = form['type'].data
            if schedule_type == 'crontab':
                model.interval = None
            elif schedule_type == 'interval':
                model.crontab = None

    def _scheduleinfo(view, context, model, name):
        """调度信息展示"""
        if model.crontab is None:
            return str(model.interval)
        else:
            return str(model.crontab)

    column_formatters = {
        'schedule': _scheduleinfo
    }

class CeleryTaskView(AuthMongView):

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
