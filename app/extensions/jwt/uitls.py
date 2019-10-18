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


from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from dateutil import tz

import arrow


def _epoch_utc_to_arrow(epoch_utc):
    """
    生成arrow时间
    """
    time = arrow.get(epoch_utc)
    return arrow.get(time.astimezone(tz.gettz('Asia/Shanghai')))


def is_token_revoked(decoded_token):
    """
    从数据库中寻找token是否被撤销
    """
    from .models import TokenBlackList
    jti = decoded_token['jti']
    try:
        token = TokenBlackList.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def add_token_to_database(encoded_token, identity_claim, custom_token_type=None):
    """
    将新的Token解码后加入到数据库

    :param custom_token_type: 自定义的token类型
    :param identity_claim: 指定的认证字段
    """
    from .models import TokenBlackList
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type'] if not custom_token_type else custom_token_type
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_arrow(decoded_token['exp'])
    revoked = False
    TokenBlackList.create(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked
    )


def revoke_token(raw_jwt):
    """
    将指定的jwt撤销
    """
    from .models import TokenBlackList

    user = raw_jwt['identity']
    jti = raw_jwt['jti']
    try:
        TokenBlackList.query.filter_by(user_identity=user,
                                       token_type='refresh',
                                       ).update({'revoked': True})
        token = TokenBlackList.query.filter_by(user_identity=user,
                                               jti=jti).one()
        token.update(revoked=True)
    except NoResultFound:
        pass
