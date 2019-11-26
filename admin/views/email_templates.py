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
    app.admin.views.email_templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    电子邮件模板的Admin管理模块
"""

from .bases import AuthModelView


class EmailTemplateView(AuthModelView):
    """电子邮件模板管理"""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    details_modal = True

    column_searchable_list = ["name"]
