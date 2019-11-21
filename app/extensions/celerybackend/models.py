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
    app.extensions.celerybackend.models
    ~~~~~~~~~~~~~~~~~~~~~~

    自定义Celery Backend models
"""

try:
    from app.extensions import mongo as db
except ImportError:
    import mongoengine as db
    setattr(db, "ArrowField", db.DateTimeField)

from uuid import UUID


class Tasks(db.Document):
    """任务表"""

    id = db.UUIDField(primary_key=True, verbose_name='任务')
    name = db.StringField(verbose_name='任务名称')
    kwargs = db.StringField(verbose_name='额外参数')
    delivery_info = db.DictField(verbose_name='分发消息')
    args = db.StringField(verbose_name='参数')
    type = db.StringField(verbose_name='类型')
    hostname = db.StringField(verbose_name='主机名')
    time_start = db.ArrowField(verbose_name='开始时间')
    acknowledged = db.BooleanField()
    worker_pid = db.IntField(verbose_name='任务进程ID')
    status = db.StringField(verbose_name='状态')
    state = db.StringField(verbose_name='执行状态')
    result = db.DynamicField(verbose_name='结果')
    date_done = db.ArrowField(verbose_name='结束时间')
    traceback = db.StringField(verbose_name='追踪信息')
    checked = db.BooleanField(verbose_name='是否已读')
    parent_id = db.UUIDField(verbose_name='父任务')
    children = db.DynamicField(verbose_name='子任务')

    meta = {'collection': 'celery_taskmeta'}

    @classmethod
    def get_by_id_str(cls, task_id):
        """根据id字符串获取对象"""
        return cls.objects.get(id=UUID(task_id))
