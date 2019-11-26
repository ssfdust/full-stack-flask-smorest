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

from flask_admin.contrib.mongoengine.filters import (
    FilterConverter as BaseFilterConverter,
)
from flask_admin.model import filters


class MongoFilterConverter(BaseFilterConverter):
    @filters.convert("ArrowField")
    def conv_arrow(self, column, name):
        return [f(column, name) for f in self.datetime_filters]

    @filters.convert("DateTimeField")
    def conv_datetime(self, column, name):
        return [f(column, name) for f in self.datetime_filters]
