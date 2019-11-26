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

from app.services.users.userinfo import handle_avator


class ExtraArgsHandler(object):
    def __init__(self, storage, args):
        self.storage = storage
        self.args = args

    def handle(self):
        func = self.__mapping__.get(self.storage.storetype, None)
        func(self.args)

    __mapping__ = {"avator": handle_avator}
