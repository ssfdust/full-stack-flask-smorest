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
    app.extensions
    ~~~~~~~~~~~~~~~~~~~~

    拓展组件
"""

from flask_babel import Babel
from flask_mail import Mail
from flask_socketio import SocketIO

from .api import api, spec_kwargs
from .celery import celery_ext
from .jwt import jwt
from .logger import Logger
from .marshal import ma
from .mongo import mongo
from .sqla import db
from .security import security

babel = Babel()
mail = Mail()
logger = Logger()
socketio = SocketIO()


def init_app(app):
    """拓展组件的初始化"""
    for ext in [db, ma, mongo, babel, logger, jwt, mail, celery_ext, socketio, security]:
        ext.init_app(app)
    api.init_app(app, spec_kwargs=spec_kwargs)
