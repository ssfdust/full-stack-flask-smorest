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
    app.backtasks.sighandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    信号处理模块

    用以处理celery中发送的信号，根据信号更新任务日志记录
"""

from celery import signals
from app.utils.formatters import celery_worker_formatter as worker_formatter


def _store_task_info(sender):
    """保存任务信息"""
    from app.extensions import celery_ext
    from app.extensions.celerybackend import models

    app = celery_ext.get_celery_app()
    inspect = app.control.inspect()
    info = inspect.query_task(sender.request.id)
    lst = worker_formatter(info)

    for item in lst:
        _id = item.pop('id')
        item['state'] = 'run'
        item.pop('type')
        models.Tasks.objects(id=_id).upsert_one(**item)


@signals.task_prerun.connect
def handle_task_prerun(sender=None, task_id=None, state=None, **kwargs):
    """处理任务预运行信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'run'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_failure.connect
def handle_task_failure(sender=None, task_id=None, state=None, **kwargs):
    """处理任务预失败信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'fail'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_success.connect
def handle_task_success(sender=None, task_id=None, state=None, **kwargs):
    """处理任务成功信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'success'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_retry.connect
def handle_task_retry(sender=None, task_id=None, state=None, **kwargs):
    """处理任务重试信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'run'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_revoked.connect
def handle_task_revoked(sender=None, task_id=None, state=None, **kwargs):
    """处理任务撤销信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'fail'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_rejected.connect
def handle_task_rejected(sender=None, task_id=None, state=None, **kwargs):
    """处理任务拒绝信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'fail'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)


@signals.task_unknown.connect
def handle_task_unknown(sender=None, task_id=None, state=None, **kwargs):
    """处理任务未知信号"""
    #  from app.extensions import celery_ext
    #  from app.extensions.celerybackend import models
    #
    #  app = celery_ext.get_celery_app()
    #  inspect = app.control.inspect()
    #  info = inspect.query_task(sender.request.id)
    #  lst = worker_formatter(info)
    #
    #  for item in lst:
    #      _id = item.pop('id')
    #      item['state'] = 'fail'
    #      item.pop('type')
    #      models.Tasks.objects(id=_id).upsert_one(**item)
    _store_task_info(sender)
