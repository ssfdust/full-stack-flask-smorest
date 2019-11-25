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

import uuid

import arrow

from pprint import pformat
from loguru import logger

def mongon_opts_str(opts):
    url = "mongodb://{username}:{password}@{host}:{port}/{db}".format(**opts)
    return url


def celery_worker_formatter(worker_info):
    '''
    e.g.


    {'celery@RedLotus':
        {
            '61421e6b-b933-412b-8f62-65425f312b69': [
                'active',
                {
                    'id': '61421e6b-b933-412b-8f62-65425f312b69',
                    'name': 'send_mail',
                    'args': '()',
                    'kwargs': '{}',
                    'type': 'send_mail',
                    'hostname': 'celery@RedLotus',
                    'time_start': 1565752238.579593,
                    'acknowledged': False,
                    'delivery_info': {
                        'exchange': '',
                        'routing_key': 'celery',
                        'priority': 0,
                        'redelivered': None
                    },
                    'worker_pid': 19696
                }
            ]
        }
    }
    '''
    from flask_babel import get_timezone

    result = []
    for _, task_info in worker_info.items():
        for _, details in task_info.items():
            state, info_dict = details
            tmp = {}
            tmp['state'] = state
            tmp.update(info_dict)
            tmp['time_start'] = arrow.get(tmp['time_start'])\
                .to(str(get_timezone()))
            _id = uuid.UUID(tmp.pop('id'))
            tmp['id'] = _id
            result.append(tmp)

    return result


def pretty_string(text, printer=logger.debug):
    """美化字符串输出"""
    for line in pformat(text).split('\n'):
        printer(line)
