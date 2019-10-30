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


def confirm_token(jti, token_type):
    from app.extensions.jwt.models import TokenBlackList
    from app.modules.auth.models import User
    from sqlalchemy.orm.exc import NoResultFound
    from flask import abort

    try:
        token = TokenBlackList.query.filter_by(
            jti=jti, token_type=token_type).one()
        if not token.revoked:
            token.update(revoked=True)
            user = User.get_by_email(token.user_identity)
            return True, user
        else:
            abort(403, "token已使用")
    except NoResultFound:
        abort(403, "token无效")


def check_confirm_token(jti, token_type):
    from app.extensions.jwt.models import TokenBlackList
    from app.modules.auth.models import User
    from sqlalchemy.orm.exc import NoResultFound
    from flask import abort

    try:
        token = TokenBlackList.query.filter_by(
            jti=jti, token_type=token_type).one()
        if not token.revoked:
            user = User.get_by_email(token.user_identity)
            return True, user
        else:
            abort(403, "token已使用")
    except NoResultFound:
        abort(403, "token无效")


def generate_confirm_token(user, token_type):
    from flask_jwt_extended import create_access_token
    from flask import current_app as app
    from app.extensions.jwt.uitls import add_token_to_database
    from datetime import timedelta

    confirm_token = create_access_token(
        identity=user.email, expires_delta=timedelta(days=1))
    add_token_to_database(confirm_token, app.config['JWT_IDENTITY_CLAIM'],
                          token_type)

    return confirm_token
