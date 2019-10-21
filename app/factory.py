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
    app.factory
    ~~~~~~~~~~~~~~~~~~~~~

    工厂模块

    用以提供库的初始化函数以及注册模块
"""

from flask_migrate import Migrate

from .extensions import init_app, db
from .extensions.flask import Flask
from .utils.formatters import mongon_opts_str

from .admin import register
from loguru import logger
import os

CONFIG_MAPPGING = {
    'development': 'app/config/development.toml',
    'production': 'app/config/production.toml',
    'testing': 'app/config/testing.toml'
}

AVAILABLE_MODULES = ['auth', 'users', 'storages',
                     'menus', 'todolist']

# 注册Admin模块
register.init()


def create_app(modules, config_name='development'):
    """
    创建app工厂

    :param              modules: list               启用模块列表
    :param              config_name: str            配置名称

    ```modules``` 启用的模块列表，模块名必须在app.modules下存在，
    将会按照顺序导入模块。

    ```config_name``` 配置名称，启用的配置名称，存在development,
    production, testing三种配置，从app/config下引用对应的TOML
    配置文件，默认是development配置。
    通过环境变量export FLASK_ENV可以覆盖掉默认的配置信息，在Docker中
    比较好用。
    """
    app = Flask("Full-Stack Flask", template_folder='app/templates',
                static_folder='app/static')

    config_type = os.environ.get('FLASK_ENV', config_name)

    app.config.from_toml(CONFIG_MAPPGING[config_type])

    logger.info(f"Server Started. Server name: {app.config['SERVER_NAME']}")

    app.config['CELERY_MONGODB_SCHEDULER_URL'] = mongon_opts_str(app.config['MONGODB_SETTINGS'])
    app.config['ENABLED_MODULES'] = modules

    init_app(app)

    # 只能在__init__.py中使用migrate
    # https://github.com/miguelgrinberg/Flask-Migrate/issues/196#issuecomment-381381242
    Migrate(app, db)
    register_modules(app)

    return app


def register_modules(app):
    """
    注册模块

    为Flask实例注册项目的主要模块
    """
    from .admin import processor
    from . import socketio, modules

    socketio.init_module()
    processor.init_processor()
    modules.init_app(app)
