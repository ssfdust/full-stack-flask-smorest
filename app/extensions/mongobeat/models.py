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

# Copyright 2018 Regents of the University of Michigan

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0
"""
    app.extensions.mongobeat
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    MongoBeat的ORM模块
"""

import datetime
from ast import literal_eval

import celery.schedules
from celery import current_app
from mongoengine import (BooleanField, DateTimeField, DictField,
                         DynamicDocument, DynamicField, EmbeddedDocument,
                         EmbeddedDocumentField, IntField, ListField,
                         StringField)


def get_periodic_task_collection():
    """获取表名"""
    if hasattr(current_app.conf, "CELERY_MONGODB_SCHEDULER_COLLECTION") \
            and current_app.conf.CELERY_MONGODB_SCHEDULER_COLLECTION:
        return current_app.conf.CELERY_MONGODB_SCHEDULER_COLLECTION  # pragma: no cover
    return "schedules"


#: Authorized values for PeriodicTask.Interval.period
PERIODS = ('days', 'hours', 'minutes', 'seconds', 'microseconds')


class PeriodicTask(DynamicDocument):
    """
    周期任务的ORM

    :attr name: 定时名称
    :attr task: 任务名称
    :attr interval: 定时
    :attr crontab: crontab
    :attr args: 参数
    :attr kwargs: 键值参数
    :attr queue: 队列
    :attr no_changes: nochanges
    :attr exchange: AMPQ的交换器
    :attr routing_key: AMPQ路由
    :attr soft_time_limit: 软时间限制
    :attr expires: 过期时间
    :attr start_after: 在某时间后运行
    :attr enabled: 启用
    :attr last_run_at: 最后运行时间
    :attr total_run_count: 总计运行次数
    :attr max_run_count: 最大运行次数
    :attr date_changed: 改变日期
    :attr description: 描述
    :attr run_immediately: 立刻运行
    """

    meta = {
        'collection': get_periodic_task_collection(),
        'allow_inheritance': True
    }

    class Interval(EmbeddedDocument):
        """
        :attr every 每（周期）
        :attr period 周期区间
        """

        meta = {'allow_inheritance': True}

        every = IntField(
            min_value=0, default=0, required=True, verbose_name='周期')
        period = StringField(choices=PERIODS, verbose_name='每')

        @property
        def schedule(self):
            return celery.schedules.schedule(
                datetime.timedelta(**{self.period: self.every}))

        @property
        def period_singular(self):
            return self.period[:-1]

        def __str__(self):
            if self.every == 1:
                return 'every {0.period_singular}'.format(self)
            return 'every {0.every} {0.period}'.format(self)

    class Crontab(EmbeddedDocument):
        """
        :attr minute 分钟
        :attr hour 小时
        :attr day_of_week 周
        :attr day_of_month 日
        :attr mouth_of_year 月
        """
        meta = {'allow_inheritance': True}

        minute = StringField(default='*', required=True, verbose_name='分钟')
        hour = StringField(default='*', required=True, verbose_name='小时')
        day_of_week = StringField(default='*', required=True, verbose_name='周')
        day_of_month = StringField(default='*', required=True, verbose_name='日')
        month_of_year = StringField(
            default='*', required=True, verbose_name='月')

        @property
        def schedule(self):
            return celery.schedules.crontab(
                minute=self.minute,
                hour=self.hour,
                day_of_week=self.day_of_week,
                day_of_month=self.day_of_month,
                month_of_year=self.month_of_year)

        def __str__(self):

            def rfield(f):
                return f and str(f).replace(' ', '') or '*'

            return '{0} {1} {2} {3} {4} (分/时/周/日/月)'.format(
                rfield(self.minute),
                rfield(self.hour),
                rfield(self.day_of_week),
                rfield(self.day_of_month),
                rfield(self.month_of_year),
            )

    name = StringField(unique=True, verbose_name='定时名称')
    task = StringField(required=True, verbose_name='任务名称')

    args = ListField(DynamicField(), verbose_name='参数')
    kwargs = DictField(verbose_name='键值参数')

    queue = StringField(verbose_name='队列')
    exchange = StringField(verbose_name='AMPQ的交换器')
    routing_key = StringField(verbose_name='AMPQ路由')
    soft_time_limit = IntField(verbose_name='软时间限制')

    expires = DateTimeField(verbose_name='过期时间')
    start_after = DateTimeField(verbose_name='在某时间后运行')
    enabled = BooleanField(default=False, verbose_name='启用')

    last_run_at = DateTimeField(verbose_name='最后运行时间')

    total_run_count = IntField(min_value=0, default=0, verbose_name='总计运行次数')
    max_run_count = IntField(min_value=0, default=0, verbose_name='最大运行次数')

    date_changed = DateTimeField(verbose_name='改变日期')
    description = StringField(verbose_name='描述')

    run_immediately = BooleanField(verbose_name='立刻运行')

    type = StringField(
        required=True, verbose_name='类型', choices=['crontab', 'interval'])
    interval = EmbeddedDocumentField(Interval, verbose_name='定时')
    crontab = EmbeddedDocumentField(Crontab, verbose_name='周期')

    # objects = managers.PeriodicTaskManager()
    no_changes = False

    def clean(self):
        """透过MongoEngine验证interval和crontab不是同时存在"""
        if self.type == 'crontab':
            self.interval = None
        else:
            self.crontab = None
        if isinstance(self.args, str):
            self.args = literal_eval(self.args)
        if isinstance(self.kwargs, str):
            self.kwargs = literal_eval(self.kwargs)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        elif self.crontab:
            return self.crontab.schedule
        else:
            raise Exception("must define interval or crontab schedule")

    def __str__(self):
        fmt = '{0.name}: {{no schedule}}'
        if self.interval:
            fmt = '{0.name}: {0.interval}'
        elif self.crontab:
            fmt = '{0.name}: {0.crontab}'
        else:
            raise Exception("must define interval or crontab schedule")
        return fmt.format(self)
