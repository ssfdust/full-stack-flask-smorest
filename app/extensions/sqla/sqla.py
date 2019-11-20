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
提供拓展后的基础对象
"""
from sqlalchemy_utils import types as ext_types
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy


def _include_ext_types(obj):
    """
    为db实例注入新类型
    """

    from .types import ArrowType
    setattr(obj, 'ArrowType', ArrowType)

    for key in ext_types.__dict__:
        if key.endswith('Type') and not hasattr(
                obj, key) and not key.endswith('ArrowType'):
            setattr(obj, key, getattr(ext_types, key))


class SQLAlchemy(BaseSQLAlchemy):
    """
    拓展SQLAlchemy模块
    """

    def __init__(self, *args, **kwargs):
        _include_ext_types(self)
        super().__init__(*args, **kwargs)


class DuplicateEntry(Exception):
    """重复的类型"""


class CharsTooLong(Exception):
    """字符过长"""
