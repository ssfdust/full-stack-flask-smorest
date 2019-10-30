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

from app.extensions.sqla import db, Model, SurrogatePK

menus_relation = db.Table('menus_relation',
                          db.Column('ancestor', db.Integer(), nullable=False),
                          db.Column('descendant', db.Integer(), nullable=False),
                          db.Column('distance', db.Integer(), nullable=False))


class Menu(Model, SurrogatePK):
    """
    菜单表

    :param      name: str(80)                       菜单名称
    :param      description: str(255)               菜单描述
    :param      pid: int                            父菜单ID
    :param      permission_id: int                  权限ID
    :param      icon: str(512)                      图标
    :param      icon: str(512)                      路径
    """

    __tablename__ = 'menus'

    name = db.Column(db.String(80), unique=True, doc='菜单名称', nullable=True)
    description = db.Column(db.String(255), doc='菜单描述')
    pid = db.Column(db.Integer(), doc='父菜单ID')
    permission_id = db.Column(db.Integer(), doc='权限ID', default=1)
    icon = db.Column(db.String(512), doc='图片')
    path = db.Column(db.String(512), doc='前端URL')
    permission = db.relationship(
        "Permission",
        primaryjoin="Permission.id == Menu.permission_id",
        foreign_keys=permission_id,
        doc='权限')
    parent = db.relationship(
        "Menu",
        primaryjoin="remote(Menu.id) == Menu.pid",
        foreign_keys=pid,
        doc="父级菜单",
    )
    children = db.relationship(
        "Menu",
        secondary="menus_relation",
        primaryjoin="Menu.id == menus_relation.c.ancestor",
        doc="子级菜单",
        secondaryjoin=("and_(Menu.id == menus_relation.c.descendant"
                       ", menus_relation.c.distance > 0)"),
        viewonly=True)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def __str__(self):
        return self.name
