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
    app.admin.regsiter
    ~~~~~~~~~~~~~~~~~~~~~~~

    注册模块

    将视图实例化，设置类别以及图标参数
"""
from flask_admin.contrib.fileadmin import FileAdmin

from app.extensions import admin, db
from app.extensions.celerybackend import models as cbackend
from app.extensions.logger import models as logm
from app.extensions.mongobeat.models import PeriodicTask
from app.modules.auth import models as authm
from app.modules.storages import models as storagem
from app.modules.users import models as userm
from app.modules.menus import models as menum

from . import views


def init():
    """初始化admin的注册模块"""
    # 首页
    admin._set_admin_index_view(views.AdminIndexView(menu_icon_type='glyph',
                                                     menu_icon_value='fa fa-home'))
    admin._views.append(views.VisitStatisticView(url='/admin/statistic/visit',
                                                 endpoint='admin.views.statistic.visit'))
    admin._views.append(views.TasksStatisticView(url='/admin/statistic/tasks',
                                                 endpoint='admin.views.statistic.tasks'))
    admin._views.append(views.IndexRedirectView(url='/',
                                                endpoint='admin.views.index'))
    admin._views.append(views.MailSendView(url='/admin/send-mail',
                                           endpoint='admin.views.sendmail'))
    admin._views.append(views.TodoListView(url='/admin/todolist',
                                           endpoint='admin.views.todolist'))
    # 用户管理
    admin.add_view(views.UserModelView(authm.User, db.session, name='用户',
                                       category='用户管理', url='/admin/users',
                                       endpoint='admin.views.users'))
    admin.add_view(views.UserInfoModelView(userm.UserInfo, db.session, name='用户详情',
                                           category='用户管理', url='/admin/userinfo',
                                           endpoint='admin.views.userinfo'))
    admin.add_view(views.RoleModelView(authm.Role, db.session, name='角色',
                                       category='用户管理', url='/admin/roles',
                                       endpoint='admin.views.roles'))
    admin.add_view(views.PermissionModelView(authm.Permission, db.session, name='权限',
                                             category='用户管理', url='/admin/permissions',
                                             endpoint='admin.views.permissions'))
    admin.add_view(views.GroupModelView(userm.Group, db.session, name='组详情',
                                        category='用户管理', url='/admin/groups',
                                        endpoint='admin.views.groups'))
    # 日志管理
    admin.add_view(views.LogModelView(logm.Log, name='访问日志', category='日志管理',
                                      url='/admin/logs', endpoint='admin.views.logs'))
    admin.add_view(views.MsgModelView(logm.Message, name='系统日志', category='日志管理',
                                      url='/admin/messages', endpoint='admin.views.messages'))
    admin.add_view(views.CeleryTaskView(cbackend.Tasks, name='任务详情', category='任务管理',
                                        url='/admin/tasks', endpoint='admin.views.tasks'))
    admin.add_view(views.CeleryScheduleView(PeriodicTask, name='调度详情', category='任务管理',
                                            url='/admin/schedules', endpoint='admin.views.schedules'))
    # 系统设置
    admin.add_view(views.MenuModelView(menum.Menu, db.session, name='菜单管理',
                                       category='系统设置', url='/admin/menus',
                                       endpoint='admin.views.menus'))
    # 文件管理
    admin.add_view(views.StorageView(storagem.Storages, db.session, url='/admin/storages',
                                     name='存储详情', category='文件管理',
                                     endpoint='admin.views.storages'))
    admin.add_view(views.GarbageView(storagem.GarbageStorages, db.session, url='/admin/garbages',
                                     name='回收站', category='文件管理',
                                     endpoint='admin.views.garbages'))
    admin.add_view(FileAdmin('uploads', url='/admin/uploads',
                             name='文件查看', category='文件管理',
                             endpoint='admin.views.uploads'))
    # 个人详情
    admin.add_view(views.ProfileView(name='个人详情', url='/admin/profile',
                                     endpoint="admin.views.profile",
                                     menu_icon_type='glyph',
                                     menu_icon_value='fa fa-id-card'))
