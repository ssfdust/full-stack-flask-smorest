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
from app.extensions.marshal.bases import BaseMsgSchema

from marshmallow import fields


class MenuSchema(ma.ModelSchema):
    """菜单"""

    children = fields.List(fields.Nested('self'))

    class Meta:
        model = models.Menu


class MenuViewSchema(BaseMsgSchema):
    """
    菜单返回内容
    """

    data = fields.List(fields.Nested(MenuSchema))
