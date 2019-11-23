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
    app.extensions.celerybackend
    ~~~~~~~~~~~~~~~~~~~~~~

    自定义Celery结果保存模块
"""

from celery.backends.mongodb import MongoBackend as BaseMongoBackend, states
from datetime import datetime
from kombu.exceptions import EncodeError
from pymongo.errors import InvalidDocument
from bson import UUIDLegacy
import uuid
import mongoengine


class MongoBackend(BaseMongoBackend):

    def _store_result(self,
                      task_id,
                      result,
                      state,
                      traceback=None,
                      request=None,
                      **kwargs):
        """保存任务的结果与状态"""
        meta = {
            '_id': UUIDLegacy(uuid.UUID(task_id)),
            'status': state,
            'result': self.encode(result),
            'date_done': datetime.utcnow(),
            'traceback': self.encode(str(traceback)),
            'checked': False,
            'children': self.encode(self.current_task_children(request),),
        }
        if request and getattr(request, 'parent_id', None):
            meta['parent_id'] = request.parent_id

        try:
            self.collection.update_one({'_id': UUIDLegacy(uuid.UUID(task_id))},
                                       {'$set': meta},
                                       upsert=True)
        except InvalidDocument as exc:
            raise EncodeError(exc)

        return result

    def _get_database(self):
        """获取数据库"""
        return mongoengine.get_db()

    def encode(self, data):
        if self.serializer == 'bson':
            # mongodb handles serialization
            if isinstance(data, str) or \
                    isinstance(data, dict) or \
                    isinstance(data, list) or \
                    isinstance(data, int):
                return data
            else:
                return str(data)

    def _get_task_meta_for(self, task_id):
        """根据task_id获取后台数据"""
        obj = self.collection.find_one({'_id': UUIDLegacy(uuid.UUID(task_id))})
        if obj:
            return self.meta_from_decoded({
                'task_id': obj['_id'],
                'status': obj['status'],
                'result': self.decode(obj['result']),
                'date_done': obj['date_done'],
                'traceback': self.decode(obj['traceback']),
                'children': self.decode(obj['children']),
            })
        return {'status': states.PENDING, 'result': None}
