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
    app.modules
    ~~~~~~~~~~~~~~~~~~~~~

    项目的核心模块，主要处理HTTP请求与返回，定义
    基本的方法以及序列化类，而核心业务则放在services
    模块。
"""


def init_app(app, module_names):
    """
    引入模块

    :param              app: Flask                  Flask实例
    :param              module_names: list          启用的模块

    ```module_names``` 启用的模块列表，模块名必须在app.modules下存在，
    将会按照顺序导入模块。
    """
    from importlib import import_module

    for module_name in module_names:
        module = import_module(f'.modules.{module_name}', 'app')
        module.init_app(app)
