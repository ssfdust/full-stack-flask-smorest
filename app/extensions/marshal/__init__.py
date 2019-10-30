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
    app.extensions.marshal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    提供拓展的flask-marshmallow模块以更好地适应项目

    使用：
    >>> from app.extensions.marshal import ma
    >>> from flask import Flask
    >>> app = Flask('')
    >>> ma.init_app(app)
    >>> class SampleSchema(ma.Schema):
            id = fields.Int()
"""

from .ma import Marshmallow
from .bases import *  # noqa

ma = Marshmallow()
