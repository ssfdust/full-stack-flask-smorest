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

from app.utils import local


class StorageCleaner(object):
    def __init__(self, orm_cls, filters=None):
        self.orm_cls = orm_cls
        self.filters = filters

    def filter(self):
        return self.orm_cls.query.filter(*self.filters)

    def clean(self):
        storages = self.filter().all()
        cnt = self.filter().count()
        for idx, storage in enumerate(storages, 1):
            storage.hard_delete()
            yield idx, cnt


class MonthExpiredCleaner(StorageCleaner):
    def filter(self):
        today = local.localdate()
        a_month_ago = today.shift(months=-1)
        return self.orm_cls.query.filter(self.orm_cls.modified < a_month_ago)
