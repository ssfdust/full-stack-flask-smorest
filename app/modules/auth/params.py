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
    app.modules.auth.params
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    用户验证参数模块
"""

from app.extensions import ma
from marshmallow import fields


class LoginParams(ma.Schema):
    '''
    登录用参数

    :attr email: str 用户邮箱
    :attr password: str 密码
    :attr captcha: str 验证码
    :attr token: str 验证码token
    '''

    email = fields.Str(required=True, allow_none=False, description='用户邮箱')
    password = fields.Str(required=True, allow_none=False, description='密码')
    captcha = fields.Str(required=True, allow_none=False, description='验证码')
    token = fields.Str(required=True, allow_none=False, description='验证token')


class JwtParam(ma.Schema):
    """
    Jwt的Token参数

    :attr token: str Jwt token
    """

    token = fields.Str(required=False, allow_none=False, description='token')


class PasswdParam(ma.Schema):
    """
    验证密码

    :attr password: str 原密码
    :attr confirm_password: str 确认密码
    """

    password = fields.Str(required=True, allow_none=False, description='密码')
    confirm_password = fields.Str(required=True, allow_none=False, description='确认密码')


class EmailParam(ma.Schema):
    """
    邮箱参数

    :attr email: str 邮箱
    """

    email = fields.Str(required=True, description='邮箱')


class CaptchaParam(ma.Schema):
    """
    验证图片Token参数

    :attr token: str 验证码token
    """

    token = fields.Str(required=True, description='随机token')
