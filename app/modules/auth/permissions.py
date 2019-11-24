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
"""
    app.modules.auth.permissions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    权限定义以及映射模块，此模块用以建立默认的
    角色权限关系，修改后通过
    `inv app.db.update-app-permissions`
    进行更新权限关系
"""


class ROLES:
    """角色字段定义"""

    SuperUser = 'SuperUser'
    User = 'User'
    UserManager = 'UserManager'
    EmailTemplateManager = 'EmailTemplateManager'
    # End Of ROLES


class PERMISSIONS:
    """权限字段定义"""

    SuperUser = 'SuperPrivilege'
    User = 'UserPrivilege'
    # UserManager
    GroupAdd = 'GroupAddPrivilege'
    GroupDelete = 'GroupDeletePrivilege'
    GroupEdit = 'GroupEditPrivilege'
    GroupQuery = 'GroupQueryPrivilege'
    UserEdit = 'UserEditPrivilege'
    # EmailTemplateManager
    EmailTemplateAdd = 'EmailTemplateAddPrivilege'
    EmailTemplateEdit = 'EmailTemplateEditPrivilege'
    EmailTemplateDelete = 'EmailTemplateDeletePrivilege'
    EmailTemplateQuery = 'EmailTemplateQueryPrivilege'
    # End Of PERMISSIONS


# 默认的角色权限映射

DEFAULT_ROLES_PERMISSIONS_MAPPING = {
    ROLES.SuperUser: [
        PERMISSIONS.SuperUser,
        PERMISSIONS.User,
        # 用户管理
        PERMISSIONS.GroupAdd,
        PERMISSIONS.GroupDelete,
        PERMISSIONS.GroupEdit,
        PERMISSIONS.GroupQuery,
        PERMISSIONS.UserEdit,
        # 电子邮件模板管理
        PERMISSIONS.EmailTemplateAdd, PERMISSIONS.EmailTemplateDelete,
        PERMISSIONS.EmailTemplateEdit, PERMISSIONS.EmailTemplateQuery,
        # End Of SuperUser
    ],
    ROLES.UserManager: [
        PERMISSIONS.GroupAdd,
        PERMISSIONS.GroupDelete,
        PERMISSIONS.GroupEdit,
        PERMISSIONS.GroupQuery,
        PERMISSIONS.UserEdit,
    ],
    ROLES.EmailTemplateManager: [
        PERMISSIONS.EmailTemplateAdd, PERMISSIONS.EmailTemplateDelete,
        PERMISSIONS.EmailTemplateEdit, PERMISSIONS.EmailTemplateQuery
    ],
    # End Of Permissions Mapping
}
