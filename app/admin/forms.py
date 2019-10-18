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
表单模块

自定义WTF表单
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from flask_admin.form.fields import DateTimeField
from flask_admin.form.upload import FileUploadInput


class TodoForm(FlaskForm):
    """
    待办表单
    """
    content = StringField('内容')
    tododue = DateTimeField('截止日期', format='%Y-%m-%d %H:%M')


class StorageForm(FlaskForm):
    """
    存储表单
    """

    name = StringField('文件名')
    filetype = StringField('文件类型')
    storetype = StringField('存储类型')
    date = DateField('文件日期')


class JustUploadField(StringField):
    """
    文件提交栏目
    """

    widget = FileUploadInput()
