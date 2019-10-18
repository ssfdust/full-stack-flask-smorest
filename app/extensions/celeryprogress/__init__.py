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


from abc import ABCMeta, abstractmethod
from decimal import Decimal

from collections import OrderedDict
from app.extensions.rpcstore import AMQPStore

PROGRESS_STATE = 'PROGRESS'


class AbtractProgressRecorder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total):
        pass


class ConsoleProgressRecorder(AbtractProgressRecorder):

    def set_progress(self, current, total):
        print('processed {} items of {}'.format(current, total))


class ProgressRecorder(AMQPStore, AbtractProgressRecorder):

    def __init__(self, task, task_id=None):
        self.task = task
        self.task_id = task_id if task_id else task.request.id
        super().__init__(key='celery_progress',
                         value=None,
                         exchange='celery_progress',
                         expires=3600*24,
                         routing_key=self.task_id)

    def set_progress(self, current, total):
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
            }
        )
        self.save()


class Progress(AMQPStore):

    _results = OrderedDict()

    def __init__(self):
        super().__init__(
            key='celery_progress',
            value=None,
            requeue=False,
            routing_key='celery',
            exchange='celery_progress',
            expires=3600*24
        )

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
                return self._results[i]
        else:
            return {
                'percent': '0'
            }


def _get_completed_progress():
    return {
        'current': 100,
        'total': 100,
        'percent': 100,
    }


def _get_unknown_progress():
    return {
        'current': 0,
        'total': 100,
        'percent': 0,
    }


progress = Progress()
