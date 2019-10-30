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

from functools import wraps
from flask import request
import ujson as json


def upload_handler(func):
    # Create the wrapped function.  This just calls the 'decorated' function
    @wraps(func)
    def wrapper(*args, **kwargs):

        results = {}
        for key, value in request.files.items():
            if value.content_type == 'application/json':
                content = value.read()
                value.stream.seek(0)
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                results[key] = json.loads(content)

        request_dic = request.__dict__

        request_dic['_cached_json'] = (results, results)
        request_dic['_cached_data'] = json.dumps(results)

        return func(*args, **kwargs)

    return wrapper
