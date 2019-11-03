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
    app.modules.sqla.types
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    自定义的sqla类型模块
"""

from __future__ import absolute_import

from collections import Iterable
from datetime import datetime

import six
from sqlalchemy import types

from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible
from dateutil import tz

import arrow


class ArrowType(types.TypeDecorator, ScalarCoercible):
    """
    自定义ArrowType，代码从sqlalchemy_utils复制而来，
    不继承的原因是改动太大，几乎全部改了。索性就复制
    过来了。
    """
    impl = types.DateTime

    def __init__(self, *args, **kwargs):
        """初始化"""
        super(ArrowType, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        """
        处理数据到数据库

        1. 替换UTC的时区为当当前时区，后转为当前时区
        2. 转换非UTC时区的时间为当前时区
        """
        from flask_babel import get_timezone
        if value:
            val = self._coerce(value)
            if val.tzinfo == tz.UTC:
                val = val.replace(tzinfo=str(get_timezone()))
            utc_val = val.to('UTC')
            return utc_val.datetime if self.impl.timezone else utc_val.naive
        return value

    def process_result_value(self, value, dialect):
        """
        从数据库中将时间转为arrow类型
        """
        from flask_babel import get_timezone
        if value:
            return arrow.get(value).to(str(get_timezone()))
        return value

    def process_literal_param(self, value, dialect):
        """
        渲染内联的支持
        """
        from flask_babel import get_timezone

        val = self._coerce(value)
        print(val)
        if val.tzinfo == tz.UTC:
            val = val.replace(tzinfo=str(get_timezone()))
        utc_val = val.to('UTC')
        return utc_val.format('YYYY-MM-DD HH:mm:ss')

    def _coerce(self, value):
        """ 预处理 """
        if isinstance(value, six.string_types):
            value = arrow.get(value)
        elif isinstance(value, Iterable):
            value = arrow.get(*value)
        elif isinstance(value, datetime):
            value = arrow.get(value)
        return value

    @property
    def python_type(self):
        """Python类型"""
        return self.impl.type.python_type
