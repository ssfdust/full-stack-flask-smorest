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
    app.admin.formaters
    ~~~~~~~~~~~~~~~~~~~~~~

    格式化模块

    控制表单以及表格的美化与显示
"""

from pprint import pformat
from flask import Markup


def json_formatter(view, context, model, name):
    '''
    格式化flask-admin中表单中的json字段，以美观显示

    :param      model: Model                ORM模型
    :param      name: str                   模型属性名

    只能用在flask-admin中的formatter中
    '''
    value = getattr(model, name)
    json_value = pformat(value, width=50)
    return Markup('<code style="width: 80%;">{}</code>'.format(json_value))


def line_formatter(view, context, model, name):
    '''
    格式化flask-admin中表格行中的json字段，以美观显示

    :param      model: Model                ORM模型
    :param      name: str                   模型属性名

    只能用在flask-admin中的formatter中
    '''
    value = getattr(model, name)
    if value:
        text = ''.join([line + '<br>' for line in value.split('\n')])
        return Markup('<pre style="width:80%;">{}</pre>'.format(text))
    else:
        return None


def short_formatter(view, context, model, name):
    '''
    格式化flask-admin中表单中的长字段，以美观显示

    :param      model: Model                ORM模型
    :param      name: str                   模型属性名

    只能用在flask-admin中的formatter中
    '''
    value = getattr(model, name)
    return str(value)[0:15]
