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

import arrow


def localnow():
    """返回本地时间"""
    from flask_babel import get_timezone
    time = arrow.now(str(get_timezone()))
    return time


def localdate():
    """返回本地日期"""
    now = localnow()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def date():
    """返回本地日期Date格式"""
    return localdate().date()
