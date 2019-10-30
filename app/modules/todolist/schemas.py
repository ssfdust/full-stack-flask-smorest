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

from . import models
from app.extensions import ma
from marshmallow import fields


class TodoItemSchema(ma.ModelSchema):
    """
    :attr               rest_time: str                  剩余时间
    :attr               level: str                      根据剩余时间

    ```level``` level用以返回给前端渲染颜色数字
    """

    rest_time = fields.Method('get_rest_time', dump_only=True)
    level = fields.Method('get_time_level', dump_only=True)

    def get_rest_time(self, obj):
        try:
            return obj.due.humanize(locale='zh')
        except ValueError:
            return obj.due.humanize(locale='en')

    def get_time_level(self, obj):
        """
        根据剩余时间获取等级

        摘录自Arrow库

        Lv1: 年
        Lv2: 月
        Lv3: 周
        Lv4: 日
        Lv5: 小时
        Lv6: 分钟
        Lv7: 过期
        """
        from app.utils.local import localnow
        diff = (obj.due - localnow()).total_seconds()
        if diff < 0:
            return 7
        elif diff < 90:
            return 6
        elif diff < 79200:
            return 5
        elif diff < 554400:
            return 4
        elif diff < 2419200:
            return 3
        elif diff < 29808000:
            return 2
        else:
            return 1

    class Meta:
        model = models.TodoItem
