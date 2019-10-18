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
    app.backtasks
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    后台任务模块

    所有的celery任务都定义在该模块中

    send_mail 发送邮件模块
    storages 存储清理模块

    celery信号处理
    sighandler 信号处理模块
"""

from app.utils.imports import import_submodules

import_submodules(locals(), __name__, __path__)
