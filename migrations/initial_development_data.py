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
数据初始化模板
"""

from sqlalchemy.orm.exc import NoResultFound
from flask_security.utils import encrypt_password

def init():
    '''
    初始化数据
    '''
    from app.modules.auth.models import User, Role, Permission
    from app.modules.users.models import UserInfo
    from app.modules.storages.models import Storages
    from app.utils import local

    su_permission = Permission.create(
        name='SuperPriviledge', description='超级用户权限')
    user_permission = Permission.create(
        name='UserPriviledge', description='普通用户权限')
    su_role = Role.create(name='SuperUser', description='超级用户角色')
    user_role = Role.create(name='User', description='用户角色')
    user_role.permissions.append(user_permission)
    su_role.permissions.append(su_permission)

    # create super user
    root = User.create(
        username='wisdom',
        password=encrypt_password('zerotoany'),
        email='wisdom@zero.any.else',
        active=True,
        confirmed_at=local.localnow())
    avator = Storages(
        name='AdminAvator.jpg',
        storetype='avator',
        saved=True,
        filetype='image/jpeg',
        path='default/AdminAvator.jpg',
        uid=1,
    )
    UserInfo.create(user=root, avator=avator)
    root.roles.append(su_role)
    root.save()


def update_permissions():
    """
    更新权限角色数据
    """
    from app.modules.auth.permissions import DEFAULT_ROLES_PERMISSIONS_MAPPING as mapping
    from app.modules.auth.models import Role, Permission
    from app.extensions import db

    for role_name, permissions in mapping.items():
        try:
            role = Role.query.filter_by(name=role_name).one()
        except NoResultFound:
            role = Role(name=role_name, description=role_name).save(False)

        for permission in permissions:
            try:
                permit = Permission.query.filter_by(name=permission).one()
            except NoResultFound:
                permit = Permission(
                    name=permission, description=permission).save(False)
            if permit not in role.permissions:
                role.permissions.append(permit)

    db.session.commit()


def init_email_templates():
    """初始化邮件模板"""
    from app.modules.email_templates.models import EmailTemplate
    template = '<p>{{ message | safe }}</p><a href="{{ url }}" target="_blank">点击访问</a>'
    for name in ["default", "confirm", "reset-password"]:
        EmailTemplate.create(name=name,
                             template=template)
