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
后台详情资料页

提供修改个人信息，提供修改个人密码
"""
from flask import request
from flask_admin.base import BaseView, expose
from flask_login import current_user
from flask_security.utils import encrypt_password


class ProfileView(BaseView):

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        """
        后台个人详情页
        """
        if request.method == 'GET':
            return self.render('admin/profile.html')
        else:
            data = request.form
            if data['sex']:
                current_user.userinfo.sex = int(data['sex'])
            if data['age']:
                current_user.userinfo.age = int(data['age'])
            if data['first_name']:
                current_user.userinfo.first_name = data['first_name']
            if data['last_name']:
                current_user.userinfo.last_name = data['last_name']

            current_user.save()
            return self.render('admin/profile.html')

    @expose('/set-passwd', methods=['PATCH'])
    def setpwd(self):
        """
        修改密码
        """
        data = request.get_json()
        if current_user.verify_and_update_password(data['oldpasswd']):
            current_user.password = encrypt_password(data['passwd'])
            current_user.save()
            return {'code': 0, 'msg': 'success'}
        else:
            return {'code': 1, 'msg': 'wrong old password'}

    @expose('/upload-avator', methods=['POST'])
    def set_avator(self):
        """
        上传头像
        """
        avator = request.files['file']
        current_user.userinfo.avator.update(_store=avator)

        return {'code': 0}
