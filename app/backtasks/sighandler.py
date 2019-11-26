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
from app.extensions.celerybackend import models
from app.extensions import celery_ext
from uuid import UUID
from app.utils.local import localnow


def _store_task_info(task_id, state="fail", **kwargs):
    """保存任务信息"""
    models.Tasks.objects(id=UUID(task_id)).upsert_one(state=state, **kwargs)


@signals.task_received.connect
def handle_task_received(request=None, **kwargs):
    """处理任务接收"""
    info = request.info()
    info["task_type"] = info.pop("type")
    task_id = info.pop("id")
    info.pop("worker_pid")
    _store_task_info(task_id, state="received", **info)


@signals.task_prerun.connect
def handle_task_prerun(task=None, task_id=None, **kwargs):
    """处理任务预运行信号"""
    with celery_ext.app_ctx:
        _store_task_info(task_id, state="run", time_start=localnow())


@signals.task_failure.connect
def handle_task_failure(sender=None, task_id=None, state=None, **kwargs):
    """处理任务预失败信号"""
    _store_task_info(task_id, state="fail")


@signals.task_success.connect
def handle_task_success(result=None, sender=None, **kwargs):
    """处理任务成功信号"""
    _store_task_info(sender.request.id, state="fail")


@signals.task_retry.connect
def handle_task_retry(sender=None, task_id=None, state=None, **kwargs):
    """处理任务重试信号"""
    _store_task_info(sender)


@signals.task_revoked.connect
def handle_task_revoked(sender=None, task_id=None, state=None, **kwargs):
    """处理任务撤销信号"""
    _store_task_info(sender)


@signals.task_rejected.connect
def handle_task_rejected(sender=None, task_id=None, state=None, **kwargs):
    """处理任务拒绝信号"""
    _store_task_info(sender, state="revoke")
