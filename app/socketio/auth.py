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
    app.socketio.auth
    ~~~~~~~~~~~~~~~~~~~
    websocket模块验证模块

    主要负责验证相关模块
"""
from flask_socketio import Namespace, emit, disconnect
from .session import SessionManager
from .decorators import auth_socket
from flask import request


class AuthNamespace(Namespace):
    """
    任务用模块
    """

    def on_connect(self):
        """连接时"""
        print('connected')

    def on_authenticate(self, data):
        """验证"""
        token = data['token']
        session = SessionManager()
        if session.check_token(token):
            session.start_session()
        else:
            print('unauthenticated')
            disconnect(request.sid)

    @auth_socket
    def on_test(self):
        emit({'data': 'Hello, World'})

    def on_disconnect(self):
        """连接丢失时"""
        user_id = request.args.get('user_id', None)
        if user_id:
            session = SessionManager(user_id)
            session.end_session()
