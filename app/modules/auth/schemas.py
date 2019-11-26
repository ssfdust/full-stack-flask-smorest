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
    app.modules.schemas
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    用户验证序列化模块
"""

from app.extensions.marshal import BaseMsgSchema, ma

from marshmallow import fields


class UserTokenSchema(ma.Schema):
    """
    登录返回Token
    """

    access_token = fields.Str(description="登录用token")
    refresh_token = fields.Str(description="刷新用token")


class RefreshTokenSchema(ma.Schema):
    """
    刷新Token
    """

    refresh_token = fields.Str(description="刷新用token")


class UserDataSchema(ma.Schema):
    """
    用户返回数据
    """

    tokens = fields.Nested(UserTokenSchema, description="token字段")


class UserViewPostSchema(BaseMsgSchema):
    """
    用户提交
    """

    data = fields.Nested(UserDataSchema, description="数据字段")


class RefreshViewPostSchema(BaseMsgSchema):
    """
    刷新token
    """

    data = fields.Nested(UserTokenSchema)
