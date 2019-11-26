#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 ssfdust RedLotus
# Author: ssfdust RedLotus
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
    app.modules.email_templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    电子邮件模板模块

    电子邮件模板
"""

from flask_smorest import Blueprint

from app.extensions import api

blp = Blueprint(
    "EmailTemplate", __name__, url_prefix="/email_templates", description="电子邮件模板"
)


def init_app(app):
    """初始化模块

    :param              app: Flask                  Flask实例
    """
    from . import models, resources  # noqa

    base_prefix = (
        app.config["MODULE_BASE_PREFIX"] if "MODULE_BASE_PREFIX" in app.config else ""
    )

    api.register_blueprint(blp, base_prefix=base_prefix)
