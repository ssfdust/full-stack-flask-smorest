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

from flask_jwt_extended import JWTManager
from flask import jsonify
from loguru import logger

from .uitls import is_token_revoked

jwt = JWTManager()


@jwt.unauthorized_loader
def unauthorized_callback(_):
    logger.error('未受权的访问')
    response = jsonify({"code": 401, "msg": "未授权的访问"})
    response.status_code = 401
    return response


@jwt.expired_token_loader
def token_expired():
    response = jsonify({"code": 402, "msg": "登录已过期"})
    logger.warning('登录过期')
    response.status_code = 402
    return response


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return is_token_revoked(decrypted_token)


@jwt.user_loader_callback_loader
def get_user(identity):
    from app.modules.auth.models import User
    return User.get_by_email(identity)


from . import models
