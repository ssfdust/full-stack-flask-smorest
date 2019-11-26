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

import os

from app.extensions.flask import Flask
from app.utils.formatters import mongon_opts_str

from .extensions import init_app
from .register import init as init_admin

CONFIG_MAPPGING = {
    "development": "app/config/development.toml",
    "production": "app/config/production.toml",
    "testing": "app/config/testing.toml",
}

ENABLED_MODULES = ["auth", "users", "storages", "menus", "todolist"]

init_admin()


def create_app(config_name="development"):
    """
    创建app工厂

    :param              config_name: str            配置名称

    ```config_name``` 配置名称，启用的配置名称，存在development,
    production, testing三种配置，从app/config下引用对应的TOML
    配置文件，默认是development配置。
    通过环境变量export FLASK_ENV可以覆盖掉默认的配置信息，在Docker中
    比较好用。
    """
    app = Flask(
        "Full-Stack Flask",
        template_folder="admin/templates",
        static_folder="admin/static",
    )

    config_type = os.environ.get("FLASK_ENV", config_name)

    app.config.from_toml(CONFIG_MAPPGING[config_type])

    app.config["SERVER_NAME"] = None

    app.config["CELERY_MONGODB_SCHEDULER_URL"] = mongon_opts_str(
        app.config["MONGODB_SETTINGS"]
    )

    init_app(app)

    # 只能在__init__.py中使用migrate
    # https://github.com/miguelgrinberg/Flask-Migrate/issues/196#issuecomment-381381242
    register_modules(app)

    return app


def register_modules(app):
    """
    注册模块

    为Flask实例注册项目的主要模块
    """
    from app import socketio
    from .processor import init_processor

    init_processor()

    socketio.init_module()
