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
    app.extensions.logger
    ~~~~~~~~~~~~~~~~~~~~~~

    日志处理模块，打印日志同时保存到MongoDb
"""

from flask import request
from loguru import logger


def save_resp(resp):
    """保存Request请求"""
    from .models import Log
    if request.method == 'GET':
        args = request.args.to_dict()
    else:
        args = request.json
    nginx_remote = 'X-Forwarded-For'
    ip = request.headers[nginx_remote] if nginx_remote in request.headers \
        else request.remote_addr
    try:
        module = request.endpoint.split('.')[0]
    except AttributeError:
        module = None
    Log(url=request.path,
        arguments=args,
        method=request.method,
        ip=ip,
        module=module if module else 'unknown',
        level='info',
        status_code=resp.status_code,
        message="请求发起").save()
    return resp


def sink(message):
    """处理来自loguru的信息"""
    from .models import Message

    msg = Message()
    msg.module = message.record['name']
    msg.line = message.record['line']
    msg.level = message.record['level']
    msg.message = str(message.record['message'])
    msg.save()


class Logger(object):
    """
    日志处理
    """

    def __init__(self, app=None):
        self._app = app
        if self._app:
            self.init_app(self._app)

    def init_app(self, app):
        self._app = app
        self._app.after_request(save_resp)
        logger.add(sink)
