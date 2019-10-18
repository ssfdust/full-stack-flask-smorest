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
    app.admin.processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    flask-security的contenxt处理模块

    单独列出，在应用初始化时需要加载，以使用
    Flask-Security来进行验证登录
"""

from flask import url_for
from flask_admin import helpers as admin_helpers
from app.extensions import admin, security


def init_processor():
    """初始化处理模块

    重新配置flask-security的processor，以让flask-admin
    调用flask-security的登录验证模块
    """
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )
