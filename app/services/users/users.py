#!/usr/bin/env python
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

from loguru import logger


def create_user(user, is_admin=False):
    """
    创建用户

    :param              user: User                  用户ORM
    :param              is_admin: bool              是否admin

    创建头像信息,创建用户基本信息
    """
    from app.modules.auth.models import Role
    from app.modules.users.models import UserInfo
    from app.modules.auth import ROLES
    from app.modules.storages.models import Storages

    if is_admin:
        su_role = Role.get_by_name(ROLES.SuperUser)
        user.roles.append(su_role)
        avator = Storages(
            name='AdminAvator.jpg',
            storetype='avator',
            saved=True,
            filetype='image/jpeg',
            path='default/AdminAvator.jpg',
            uid=1,
        )
    else:
        roles = Role.get_by_user_default()
        user.roles = roles
        avator = Storages(
            name='DefaultAvator.jpg',
            storetype='avator',
            saved=True,
            filetype='image/jpeg',
            path='default/DefaultAvator.jpg',
            uid=1,
        )
    UserInfo(user=user, avator=avator).save(False)


class UserFactory(object):
    """
    用户工厂

    用于操作用户组的删改，删除用户组的同时，删除用户对应
    角色增加用户组的同时，增加用户相应角色
    """

    def __init__(self, user):
        self.user = user
        self.added_groups = []
        self.deleted_groups = []
        self.parse_groups()

    def parse_groups(self):
        """
        处理组关系
        """
        from app.extensions import db

        state = db.inspect(self.user)
        groups_hist = state.attrs.groups.history

        if groups_hist.has_changes():
            self.added_groups = groups_hist.added if groups_hist.added else []
            self.deleted_groups = groups_hist.deleted if groups_hist.deleted else []

    def hanlde_groups_change(self):
        """
        处理组改变
        """
        self.delete_permissions()
        self.add_permissions()

    def delete_permissions(self):
        """
        删除所有组权限
        """
        from app.modules.users.models import groups_roles, groups_users
        from app.modules.auth.models import roles_users, db

        if not self.deleted_groups:
            return

        sql = f"""
            DELETE
            FROM
            {roles_users} ru
            using (
                SELECT a.role_id,
                       gu.user_id
                FROM {groups_roles} a
                JOIN {groups_users} gu ON gu.group_id = a.group_id
                WHERE a.group_id in :group_ids and gu.user_id = :user_id
            ) sub
            WHERE ru.role_id = sub.role_id AND ru.user_id = sub.user_id
        """
        db.session.execute(
            sql, {
                'group_ids': tuple([g.id for g in self.deleted_groups]),
                'user_id': self.user.id
            })

    def add_permissions(self):
        """
        新增组权限
        """
        from app.modules.users.models import groups_roles
        from app.modules.auth.models import roles_users, db

        if not self.added_groups:
            return

        sql = f"""
            INSERT INTO
            {roles_users} (role_id, user_id)
            SELECT a.role_id, :user_id
            FROM {groups_roles} a
            JOIN {roles_users} ru ON ru.role_id = a.role_id
            WHERE a.group_id in :group_ids and ru.role_id is null
        """
        try:
            db.session.execute(
                sql, {
                    'group_ids': tuple([g.id for g in self.added_groups]),
                    'user_id': self.user.id
                })
            logger.info('创建组uid: %s数据成功' % self.user.id)
        except Exception as e:
            logger.error('add groups error')
            raise e
