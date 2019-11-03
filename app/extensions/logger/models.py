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
    app.extensions.logger.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    日志ORM模块
"""

from app.extensions import mongo as db
from app.utils.local import localnow


class Log(db.Document):
    """
    请求日志表

    :attr arguments:DynamicField 参数
    :attr message:StringField 消息
    :attr created:ArrowField 创建时间
    :attr method:StringField 方法
    :attr module:StringField 模块
    :attr status_code:IntField 状态码
    :attr url:StringField 地址
    :attr ip:StringField ip地址
    :attr level:StringField 等级
    """

    arguments = db.DynamicField(verbose_name='参数')
    message = db.StringField(verbose_name='消息')
    created = db.ArrowField(verbose_name='创建时间', default=localnow)
    method = db.StringField(verbose_name='方法')
    module = db.StringField(verbose_name='模块')
    status_code = db.IntField(verbose_name='状态码')
    url = db.StringField(verbose_name='地址')
    ip = db.StringField(verbose_name='ip地址')
    level = db.StringField(verbose_name='等级')


class Message(db.Document):
    """
    消息日志表

    :attr module:StringField 模块
    :attr line:IntField 行号
    :attr level:StringField 日志等级
    :attr message:StringField 内容
    :attr created:ArrowField 创建时间
    """

    module = db.StringField(verbose_name='模块')
    line = db.IntField(verbose_name='行号')
    level = db.StringField(verbose_name='日志等级')
    message = db.StringField(verbose_name='内容')
    created = db.ArrowField(default=localnow, verbose_name='创建时间')
