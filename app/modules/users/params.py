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

from . import schemas
from .schemas import fields
from marshmallow import post_load


class UserInfoParam(schemas.UserInfoSchema):
    """
    用户信息参数
    """

    class Meta(schemas.UserInfoSchema.Meta):
        exclude = ['id']


class GroupInfoParam(schemas.GroupSchema):
    """
    组信息参数
    """

    class Meta(schemas.GroupSchema.Meta):
        exclude = ['parent', 'users', 'children', 'roles', 'id']


class UserListByIdParam(schemas.ma.Schema):
    """
    处理形如
    {'users': [1, 2, 3, 4]}
    json格式
    """

    users = fields.List(fields.Int, description='用户ID列表')

    @post_load
    def load_users(self, data, **kw):
        from ..auth.models import User

        users = User.query.filter(User.id.in_(data['users'])).all()

        return users
