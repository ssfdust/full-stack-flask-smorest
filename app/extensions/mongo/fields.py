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
    app.modules.mongo.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    自定义的MongoEngine类型模块
"""

from __future__ import absolute_import

from collections import Iterable
from mongoengine.base import BaseField

from datetime import datetime
from dateutil import tz

import arrow


class ArrowField(BaseField):
    """
    自定义ArrowType，支持arrow类型
    同时处理UTC时间
    """

    def validate(self, value):
        new_value = self.to_mongo(value)
        if not isinstance(new_value, datetime):
            self.error(u'cannot parse date "%s" type: %s' %
                       (value, type(value)))

    def to_mongo(self, data):
        """
        处理数据到数据库

        1. 替换UTC的时区为当当前时区，后转为当前时区
        2. 转换非UTC时区的时间为当前时区
        """
        from flask_babel import get_timezone as gttz
        if data:
            value = self._preload(data)
            if value.tzinfo == tz.UTC:
                value = value.replace(tzinfo=gttz())
            utc_value = value.to('UTC')
            return utc_value.datetime
        return data

    def _preload(self, value):
        """ 预处理 """
        if isinstance(value, datetime):
            value = arrow.get(value)
        elif isinstance(value, str):
            value = arrow.get(value)
        elif isinstance(value, Iterable):
            value = arrow.get(*value)
        return value

    def to_python(self, value):
        """
        从数据库中将时间转为arrow类型
        """
        from flask_babel import get_timezone
        if value:
            return arrow.get(value).to(str(get_timezone()))
        return value

    def prepare_query_value(self, op, value):
        return super(ArrowField,
                     self).prepare_query_value(op, self.to_mongo(value))
