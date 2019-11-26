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
    app.mongo.mongoengine
    ~~~~~~~~~~~~~~~~~~~~~~~

    自定义的MongoEngine引擎
"""

from flask_mongoengine import MongoEngine as BaseMongoEngine


def _include_ext_types(obj):
    """注入新类型"""
    from .fields import ArrowField

    setattr(obj, "ArrowField", ArrowField)


class MongoEngine(BaseMongoEngine):
    def __init__(self, *args, **kwargs):
        _include_ext_types(self)
        super().__init__(*args, **kwargs)
