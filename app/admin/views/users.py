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
用户管理模块

用户管理
用户信息管理
用户角色管理
用户权限管理
"""
from flask import Markup, flash, redirect, url_for
from flask_admin.base import expose
from flask_admin.helpers import get_form_data
from flask_security.utils import encrypt_password

from .bases import AuthModelView


class UserModelView(AuthModelView):
    """
    用户管理

    由于权限和用户是viewonly属性，所以权限只能是查看
    """

    column_searchable_list = ['id', 'username', 'email']

    column_editable_list = ['active', 'deleted']

    column_exclude_list = ['password']

    column_list = ['username', 'email', 'active', 'confirmed_at', 'send_mail']

    column_labels = {'send_mail': '邮件验证'}

    def _send_mail(view, context, model, name):
        """验证邮件栏目"""

        if model.confirmed_at:
            return '已验证'

        # render a form with a submit button for student, include a hidden field for the student id
        # note how checkout_view method is exposed as a route below
        mail_url = url_for('.send_mail_view')

        _html = '''
            <form action="{mail_url}" method="POST">
                <input id="user_id" name="user_id"  type="hidden" value="{user_id}">
                <button class="btn btn-info" type='submit'>发送邮件</button>
            </form
        '''.format(mail_url=mail_url, user_id=model.id)

        return Markup(_html)

    @expose('send_mail', methods=['POST'])
    def send_mail_view(self):
        """发送验证邮件"""
        from app.services.auth.confirm import generate_confirm_token
        from app.backtasks.send_mail import send_mail

        return_url = self.get_url('.index_view')
        form = get_form_data()

        if not form:
            flash('无法获取表单', 'error')
            return redirect(return_url)

        uid = form['user_id']

        user = self.model.get_by_id(uid)
        token = generate_confirm_token(user, 'confirm')
        send_mail.delay(user.email, '验证邮箱', {'token': token}, 'emails/confirm.html')
        flash('验证邮件已发送')

        return redirect(return_url)

    column_formatters = {
        'send_mail': _send_mail
    }

    form_excluded_columns = ['password', 'created', 'modified']

    form_widget_args = {
        'permissions': {
            'disabled': True
        },
    }

    def on_model_change(self, form, model, is_created):
        """创建新账户时设置密码"""
        from app.services.users import create_user
        from app.services.users.users import UserFactory

        factory = UserFactory(model)
        factory.hanlde_groups_change()

        if is_created is True:
            model.password = encrypt_password('123456')
            create_user(model)

        super().on_model_change(form, model, is_created)


class UserInfoModelView(AuthModelView):
    """
    用户信息管理
    """

    column_searchable_list = ['uid']

    form_excluded_columns = ['uid', 'avator_id']

    column_exclude_list = ['uid', 'avator_id']

    def _sex_label(view, context, model, name):
        return model.sex_label

    form_choices = {
        'sex': [
            ('1', '男'),
            ('2', '女')
        ]
    }

    def _avatorinfo(view, context, model, name):
        """显示头像信息"""
        return Markup('<img src="%s" style="width: 30px; height: 30px;border-radius: 30px;">' %
                      url_for('admin.views.storages.storage_file', file_id=model.avator_id)
                      )

    column_formatters = {
        'avator': _avatorinfo,
        'sex': _sex_label
    }


class RoleModelView(AuthModelView):
    """用户角色管理"""

    column_searchable_list = ['name']
    column_editable_list = ['user_default', 'group_default']
    column_editable_list += AuthModelView.column_editable_list


class PermissionModelView(AuthModelView):
    """用户权限管理
    由于权限和用户是viewonly属性，所以用户只能是查看
    """

    column_searchable_list = ['name']

    form_widget_args = {
        'users': {
            'disabled': True
        },
    }


class GroupModelView(AuthModelView):
    """
    用户组管理
    """

    column_searchable_list = ['name']
    column_exclude_list = ['pid']
    form_excluded_columns = ['pid'] + AuthModelView.form_excluded_columns

    form_widget_args = {
        'children': {
            'disabled': True
        },
    }

    def on_model_change(self, form, model, is_created):
        """创建修改组时"""
        from app.services.users.groups import GroupFactory

        group_factory = GroupFactory(model)

        if group_factory.check_soft_delete():
            return

        if is_created is True:
            group_factory.add_group()
        else:
            group_factory.modify_group()

        super().on_model_change(form, model, is_created)

    def delete_model(self, model):
        """删除组时"""
        from app.services.users.groups import GroupFactory
        from app import db

        group_factory = GroupFactory(model)
        group_factory.delete_group(soft_delete=False)
        db.session.commit()
        self.after_model_delete(model)

        return True
