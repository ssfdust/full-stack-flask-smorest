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
    app.extensions.celeryprogress
    ~~~~~~~~~~~~~~~~~~~~~~

    celery 进度条模块
"""

from abc import ABCMeta, abstractmethod
from decimal import Decimal

from collections import OrderedDict
from app.extensions.rpcstore import AMQPStore

PROGRESS_STATE = 'PROGRESS'


class AbtractProgressRecorder(object):
    """抽象Recorder"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total):
        pass  # pragma: no cover


class ProgressRecorder(AMQPStore, AbtractProgressRecorder):
    """实现Recorder"""

    def __init__(self, task, task_id=None):
        """初始化进度条"""
        self.task = task
        self.task_id = task_id if task_id else task.request.id
        super().__init__(
            key='celery_progress',
            value=None,
            exchange='celery_progress',
            expires=3600 * 24,
            routing_key="celery_progress")

    def set_progress(self, current, total):
        """设置进度条信息"""
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        self.value = dict(
            task_id=self.task_id,
            state=PROGRESS_STATE,
            meta={
                'current': current,
                'total': total,
                'percent': percent,
            })
        self.save()


class Progress(AMQPStore):
    """读取进度"""

    _results = OrderedDict()

    def __init__(self):
        super().__init__(
            key='celery_progress',
            value=None,
            routing_key='celery_progress',
            exchange='celery_progress',
            expires=3600 * 24)

    def _get_info(self):
        self.reload()
        for item in self.values:
            if len(self._results) >= 5:
                self._results.popitem(False)
            self._results[item['task_id']] = item['meta']

    def get_info(self, task_id):
        self._get_info()
        for i in self._results:
            if i == task_id:
                ret = self._results[i]
                break
        else:
            ret = {'percent': 0}

        return ret


progress = Progress()
