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


from app.extensions.sqla import SurrogatePK, Model, db


class TokenBlackList(SurrogatePK, Model):
    """
    Token Black List Table

    :attr user_identity: str(50) 验证信息
    :attr jit: str(36) 36位jti信息
    :attr revoked: bool 是否撤销
    :attr token_type: str(10) token类型
    :attr expires: Arrow 过期时间
    """
    __tablename__ = "jwt_token_blacklist"

    user_identity = db.Column(db.String(50), nullable=False)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    expires = db.Column(db.ArrowType(True), nullable=False)
