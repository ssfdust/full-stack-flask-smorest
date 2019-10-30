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

from app.extensions.sqla import Model, SurrogatePK, db

groups_users = db.Table('groups_users',
                        db.Column('group_id', db.Integer(), nullable=False),
                        db.Column('user_id', db.Integer(), nullable=False))

groups_roles = db.Table('groups_roles',
                        db.Column('group_id', db.Integer(), nullable=False),
                        db.Column('role_id', db.Integer(), nullable=False))

groups_relation = db.Table(
    'groups_relation', db.Column('ancestor', db.Integer(), nullable=False),
    db.Column('descendant', db.Integer(), nullable=False),
    db.Column('distance', db.Integer(), nullable=False))


class Group(Model, SurrogatePK):
    """
    组别表

    :attr name: str(80) 组名称
    :attr description: str(255) 组描述
    :attr pid: int 父组ID
    :attr roles: Role 组默认角色
    :attr users: User 组成员
    :attr parent: Group 父组
    :attr children: Group 子组
    """

    __tablename__ = 'groups'

    name = db.Column(db.String(80), unique=True, doc='组名称', nullable=True)
    description = db.Column(db.String(255), doc='组描述')
    pid = db.Column(db.Integer(), doc='父组ID')
    users = db.relationship(
        "User",
        secondary="groups_users",
        primaryjoin="Group.id == groups_users.c.group_id",
        secondaryjoin="User.id == groups_users.c.user_id",
        doc="组下用户",
        foreign_keys="[groups_users.c.group_id,"
        "groups_users.c.user_id]",
        backref=db.backref('groups', lazy='dynamic', doc='所有组'),
        lazy="joined")
    roles = db.relationship(
        "Role",
        secondary="groups_roles",
        primaryjoin="Group.id == groups_roles.c.group_id",
        secondaryjoin="Role.id == groups_roles.c.role_id",
        doc="组下默认角色",
        foreign_keys="[groups_roles.c.group_id,"
        "groups_roles.c.role_id]",
        backref=db.backref('groups', lazy='dynamic', doc='所属组'),
        cascade='all,delete',
        lazy='joined')
    parent = db.relationship(
        "Group",
        primaryjoin="remote(Group.id) == Group.pid",
        foreign_keys=pid,
        doc="父节点")
    children = db.relationship(
        "Group",
        secondary="groups_relation",
        primaryjoin="Group.id == groups_relation.c.ancestor",
        doc="子组别",
        secondaryjoin=("and_(Group.id == groups_relation.c.descendant,"
                       "groups_relation.c.distance > 0)"),
        viewonly=True)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def setup_roles(self):
        """
        设置默认组角色
        """
        from app.modules.auth.models import Role

        if self.roles:
            return

        roles = Role.query.filter_by(group_default=True).all()
        self.roles = roles

    def __str__(self):
        return self.name


class UserInfo(SurrogatePK, Model):
    """
    用户信息表

    :attr avator_id: int 用户头像ID
    :attr uid: int 用户ID
    :attr avator: Storages 用户头像
    :attr user: User 关联用户
    :attr sex: int 性别
    :attr age: int 年龄
    :attr first_name: str(80) 姓
    :attr second_name: str(80) 名
    """
    from app.modules.storages.models import Storages
    from marshmallow.validate import OneOf, Range

    __tablename__ = "userinfo"

    avator_id = db.Column(
        db.Integer, doc='头像ID', info={'marshmallow': {
            'dump_only': True
        }})
    uid = db.Column(
        db.Integer, doc='用户ID', info={'marshmallow': {
            'dump_only': True
        }})
    avator = db.relationship(
        "Storages",
        primaryjoin="Storages.id == UserInfo.avator_id",
        foreign_keys=avator_id,
        doc='头像',
        lazy='joined',
        info={'marshmallow': {
            'dump_only': True
        }})
    sex = db.Column(
        db.Integer,
        doc='性别',
        default=1,
        info={
            'marshmallow': {
                'validate': [OneOf([1, 2])],
                'allow_none': False,
                'required': True
            }
        })
    age = db.Column(
        db.Integer,
        doc='年龄',
        info={
            'marshmallow': {
                'allow_none': False,
                'validate': [Range(1, None)],
                'required': True
            }
        })
    first_name = db.Column(
        db.String(80),
        doc='姓',
        info={'marshmallow': {
            'allow_none': False,
            'required': True
        }})
    last_name = db.Column(
        db.String(80),
        doc='名',
        info={'marshmallow': {
            'allow_none': False,
            'required': True
        }})
    user = db.relationship(
        "User",
        doc='用户',
        primaryjoin="User.id == UserInfo.uid",
        foreign_keys=uid,
        backref=db.backref(
            'userinfo',
            uselist=False,
            lazy='joined',
            info={'marshmallow': {
                'column': ['avator_id']
            }}),
        info={'marshmallow': {
            'dump_only': True
        }})

    def __str__(self):
        return self.user.username

    @property
    def sex_label(self):
        """性别标签"""
        labels = {1: '男', 2: '女'}
        try:
            return labels[self.sex]
        except KeyError:
            return '未填写'
