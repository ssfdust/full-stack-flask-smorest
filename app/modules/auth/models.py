#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    app.modules.auth.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    权限登录模块ORM
"""

from flask_security import RoleMixin, UserMixin

from app.extensions.sqla import Model, SurrogatePK, db

permission_roles = db.Table(
    'permission_roles',
    db.Column('permission_id', db.Integer(), nullable=False),
    db.Column('role_id', db.Integer(), nullable=False),
)

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), nullable=False),
                       db.Column('role_id', db.Integer(), nullable=False))


class Permission(Model, RoleMixin, SurrogatePK):
    """
    角色表

    :attr name: str(80) 权限名称
    :attr description: str(255) 权限描述
    :attr roles: Role 所有角色
    :attr users: User 所有用户
    """

    __tablename__ = 'permissions'

    name = db.Column(db.String(80), unique=True, doc='权限名称', nullable=True)
    description = db.Column(db.String(255), doc='权限描述')

    @classmethod
    def get_by_name(cls, name):  # pragma: no cover
        return cls.query.filter_by(name=name).first()

    def __str__(self):  # pragma: no cover
        return self.name


class Role(Model, RoleMixin, SurrogatePK):
    """
    角色表

    :attr name: str(80) 角色名称
    :attr description: str(255) 角色描述
    :attr permissions: Permission 所有权限
    :attr user_default: bool 用户默认角色
    :attr group_default: bool 组默认角色
    """

    __tablename__ = 'roles'

    name = db.Column(db.String(80), unique=True, doc='角色名称', nullable=True)
    description = db.Column(db.String(255), doc='角色描述')
    user_default = db.Column(db.Boolean, doc='用户默认角色', default=False)
    group_default = db.Column(db.Boolean, doc='组默认角色', default=False)
    permissions = db.relationship(
        'Permission',
        secondary=permission_roles,
        doc='所有权限',
        primaryjoin="foreign(permission_roles.c.role_id) == Role.id",
        secondaryjoin="foreign(permission_roles.c.permission_id) == Permission.id",
        backref=db.backref('roles', lazy='dynamic', doc='所有角色'))

    @classmethod
    def get_by_name(cls, name):  # pragma: no cover
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_by_user_default(cls):  # pragma: no cover
        return cls.query.filter_by(user_default=True).all()  # pragam: no cover

    def get_permissions(self):  # pragma: no cover
        """
        获取权限

        兼容flask-security
        """
        return set(permission.name for permission in self.permissions)

    def __str__(self):  # pragma: no cover
        return self.name


user_permissions = db.join(roles_users, permission_roles,
                           roles_users.c.role_id == permission_roles.c.role_id)


class User(Model, UserMixin, SurrogatePK):
    """
    用户表

    :attr username: str(255) 用户名
    :attr email: str(255) 用户邮箱
    :attr password: str(255) 用户密码
    :attr active: bool 是否启用
    :attr confirmed_at: arrow 确认时间
    :attr roles: Role 角色
    :attr permissions: Permission 权限
    """

    __tablename__ = 'users'

    username = db.Column(db.String(255), nullable=False, doc='用户名')
    email = db.Column(db.String(255), nullable=False, unique=True, doc='用户邮箱')
    password = db.Column(db.String(255), nullable=False, doc='用户密码')
    active = db.Column(db.Boolean(), doc='启用')
    confirmed_at = db.Column(db.ArrowType(), doc='确认时间')
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        doc='所有角色',
        primaryjoin="foreign(roles_users.c.user_id) == User.id",
        secondaryjoin="foreign(roles_users.c.role_id) == Role.id",
        backref=db.backref('users', lazy='dynamic', doc='所有用户'),
        info={'marshmallow': {
            'dump_only': True,
            'column': ['id', 'name']
        }})
    permissions = db.relationship(
        'Permission',
        secondary=user_permissions,
        doc='权限',
        primaryjoin="User.id == roles_users.c.user_id",
        secondaryjoin="Permission.id == permission_roles.c.permission_id",
        backref=db.backref('users', doc='用户', lazy='dynamic'),
        viewonly=True,
        info={'marshmallow': {
            'dump_only': True,
            'column': ['id', 'name']
        }})

    @classmethod
    def get_by_email(cls, email):  # pragma: no cover
        '''
        根据邮箱获取用户
        '''
        return cls.query.filter_by(deleted=False, email=email).first()

    def __str__(self):  # pragma: no cover
        return self.email

    @property
    def nickname(self):
        if self.userinfo.first_name and self.userinfo.last_name:
            return self.userinfo.first_name + self.userinfo.last_name
        elif self.username:
            return self.username
        else:
            return self.email
