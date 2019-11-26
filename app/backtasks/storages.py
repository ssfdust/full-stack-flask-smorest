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
    app.backtasks.storages
    ~~~~~~~~~~~~~~~~~~~~~~~

    存储清理模块

    清理过期文件
    实时进度条测试
"""

from app.extensions import celery_ext as celery
from loguru import logger


@celery.task(
    bind=True,
    name="清理内容",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=600,
)
def clean_expired_storages(self):
    """
    清理过期文件
    """
    from app.extensions.celeryprogress import ProgressRecorder
    from app.services.storages.clear import MonthExpiredCleaner
    from app.modules.storages.models import GarbageStorages

    progress_recorder = ProgressRecorder(self)
    cleaner = MonthExpiredCleaner(GarbageStorages)
    logger.info("开始清理冗余数据")
    for prg, total in cleaner.clean():
        progress_recorder.set_progress(prg, total)


@celery.task(
    bind=True,
    name="进度条测试",
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=1000,
)
def progress_bar(self):
    """
    进度条测试
    """
    from app.extensions.celeryprogress import ProgressRecorder
    from time import sleep

    progress_recorder = ProgressRecorder(self)
    for i in range(4):
        sleep(1)
        progress_recorder.set_progress(i, 100)
