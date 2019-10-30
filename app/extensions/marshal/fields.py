#!/usr/bin/env python
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
    app.extensions.marshal.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    自定义的Marshmallow Filed模块
"""

from marshmallow import fields
import arrow


class ArrowField(fields.DateTime):
    """
    ArrowType的ArrowField

    并没有对时区进行处理，因为时区的处理交由
    给了ArrowType进行处理，会自行转换时区。
    """

    def _deserialize(self, value, attr, data, **kwargs):
        """将字符串转为arrow类型"""
        if not value:
            raise self.make_error(
                "invalid", input=value, obj_type=self.OBJ_TYPE)

        target = arrow.get(value)

        return target
