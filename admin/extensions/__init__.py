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
    admin.extensions
    ~~~~~~~~~~~~~~~~~~~~

    拓展组件
"""

from flask_babel import Babel
from flask_mail import Mail
from flask_socketio import SocketIO

from app.extensions.celery import celery_ext
from app.extensions.marshal import ma
from app.extensions.mongo import mongo
from app.extensions.sqla import db

from .admin import admin
from app.extensions.security import security

babel = Babel()
mail = Mail()
socketio = SocketIO()


def init_app(app):
    """拓展组件的初始化"""
    for ext in [db, ma, mongo, babel, admin, security, mail, celery_ext]:
        ext.init_app(app)
