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


class GroupFactory():
    """
    组操作工厂，实现对组的递归操作

    包括对组的父子级的操作：
    实现对组员的角色操作，添加成员时添加相应权限，
    删除组员时，撤销相应权限，当删除组的时候，
    删除所有子组以及子成员之间的关系，并撤销全部组
    以及子组权限。
    """

    def __init__(self, group):
        self.group = group
        self.deleted_users = []
        self.added_users = []
        self.parse_group_members()

    def check_soft_delete(self):
        """
        检查是否被软删除，并执行软删除
        """
        from app.extensions import db
        state = db.inspect(self.group)
        if state.attrs.deleted.history.has_changes() and self.group.deleted:
            self.delete_group()
            return True
        return False

    def parse_group_members(self):
        """
        处理组成员

        获取到组的成员添加/删改情况，为添加删除权限，
        做处理
        """
        from app.extensions import db
        state = db.inspect(self.group)
        user_hist = state.attrs.users.history
        self.added_users = user_hist.added if user_hist.added else []
        self.deleted_users = user_hist.deleted if user_hist.deleted else []

    def handle_user_roles(self):
        """
        处理用户角色

        为新用户添加角色，为删除的用户删除角色
        """
        from app.modules.auth.models import roles_users, db
        from itertools import product

        # 组装sql
        if self.deleted_users:
            deleted_sql = db.delete(roles_users).where(
                db.and_(
                    roles_users.c.role_id.in_([r.id for r in self.group.roles]),
                    roles_users.c.user_id.in_(
                        [u.id for u in self.deleted_users])))
            db.session.execute(deleted_sql)

        if self.added_users:
            producted_added_rv = [{
                'role_id': r.id,
                'user_id': u.id
            } for r, u in product(self.group.roles, self.added_users)]
            added_sql = db.insert(roles_users, producted_added_rv)
            db.session.execute(added_sql)

    def add_group(self):
        """
        新增一个组别

        新增一个组别，并为组别建立树，为组设置默认权限。
        若组别中含有成员则为成员全部添加默认权限。
        """
        from app.modules.users.models import db
        from app.utils.db import ClosureTable

        db.session.add(self.group)
        # 设置默认角色
        self.group.setup_roles()

        # 处理角色权限
        self.handle_user_roles()

        db.session.flush()
        cl_tb = ClosureTable(self.group)
        # 建立树
        cl_tb.insert_node()

        return self.group

    def modify_group(self):
        """
        修改一个组

        修改一个组，并为组调整树，调整直属成员权限
        """
        from app.modules.users.models import db
        from app.utils.db import ClosureTable

        # 处理角色权限
        self.handle_user_roles()

        # 修改树关系
        cl_tb = ClosureTable(self.group)
        cl_tb.move_tree()

        db.session.flush()

        return self.group

    def delete_group(self, soft_delete=True):
        """
        删除一个组

        删除一个组，删除所有子节点，并删除节点下所有
        子节点成员权限
        必需先删除权限,再解除成员关系,再删除树节点
        """
        from app.utils.db import ClosureTable

        self.delete_subgroup_permissions()

        self.delete_subgroup_members(soft_delete)

        cl_tb = ClosureTable(self.group)
        cl_tb.delete_subtree(soft_delete=soft_delete)

    def delete_subgroup_permissions(self):
        """
        删除所有子组成员权限
        """
        from app.modules.users.models import Group, groups_roles, groups_users
        from app.modules.auth.models import roles_users, db

        sql = f"""
            DELETE
            FROM
            {roles_users} ru
            using (
                SELECT a.role_id,
                       gu.user_id
                FROM {Group.__tablename__} g
                JOIN {groups_roles} a ON g.id = a.group_id
                JOIN {groups_users} gu ON gu.group_id = g.id
                WHERE g.id in (
                    select descendant from {Group.__tablename__}_relation
                    where ancestor = :id
                )
            ) sub
            WHERE ru.role_id = sub.role_id AND ru.user_id = sub.user_id
        """
        db.session.execute(sql, {'id': self.group.id})

    def delete_subgroup_members(self, soft_delete=True):
        """
        解除所有子组成员关系
        """
        from app.modules.users.models import Group, groups_users, db
        if not soft_delete:
            soft_delete_arg = " AND distance > 0"
        else:
            soft_delete_arg = ""

        sql = f"""
            DELETE FROM {groups_users} gu
            WHERE gu.group_id in (
                select descendant from {Group.__tablename__}_relation
                where ancestor = :id{soft_delete_arg}
            )
        """
        # ORM删除时自动处理连接关系
        # 只有当手动处理时取消所有节点连接
        db.session.execute(sql, {'id': self.group.id})
