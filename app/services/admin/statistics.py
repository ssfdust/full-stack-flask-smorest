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
    app.services.admin.statistics
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Admin后台统计模块
"""

def get_main_page_info():
    """获取首页统计信息

    :return             info: Dict                  统计信息
    """
    from app.extensions.celerybackend import models
    from app.extensions.logger.models import Log
    from app.modules.auth.models import User
    from app.utils import local

    task_cnt = models.Tasks.objects(time_start__gte=local.localdate()).count()
    user_cnt = User.query.count()
    new_user_cnt = User.query.filter(User.created > local.localdate()).count()
    log_cnt = Log.objects(created__gte=local.localdate(),
                          module__nin=['static', 'admin', 'unknown']).count()
    task_success_cnt = models.Tasks.objects(time_start__gte=local.localdate(),
                                            state='success').count()
    task_run_cnt = models.Tasks.objects(time_start__gte=local.localdate(),
                                        state='run').count()
    task_fail_cnt = models.Tasks.objects(time_start__gte=local.localdate(),
                                         state='fail').count()
    if task_success_cnt == 0:
        task_success = 0
    else:
        task_success = int(task_success_cnt / task_cnt * 100)

    if task_run_cnt == 0:
        task_run = 0
    else:
        task_run = int(task_run_cnt / task_cnt * 100)

    if task_fail_cnt == 0:
        task_fail = 0
    else:
        task_fail = int(task_fail_cnt / task_cnt * 100)

    info = {
        'task': task_cnt,
        'user': user_cnt,
        'new_user': new_user_cnt,
        'log': log_cnt
    }

    return info, task_success, task_run, task_fail

def count_last_week_dayli_requests():
    '''
    获取上周的每日流量
    '''
    from flask_babel import get_timezone
    from app.extensions.logger.models import Log
    from app.utils import local

    project = {
        "$project": {
            "cdate": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$created",
                    "timezone": str(get_timezone())
                }
            },
            "day": {
                "$dayOfYear": {
                    "timezone": str(get_timezone()),
                    "date": "$created"
                }
            }
        }
    }
    group = {
        "$group": {
            "_id": "$day",
            "date": {
                "$first": "$cdate"
            },
            "cnt": {
                "$sum": 1
            }
        }
    }
    sort = {
        "$sort": {
            '_id': 1
        }
    }
    a_week_ago = local.localdate().shift(weeks=-1)
    cursor = Log.objects(created__gte=a_week_ago,
                         module__nin=['static', 'admin', 'unknown']).aggregate(project, group, sort)

    data = [i for i in cursor]
    labels = [i['date'] for i in data]
    cnts = [i['cnt'] for i in data]

    return {'labels': labels, 'cnts': cnts}

def count_last_week_method_requests():
    '''
    获取上周的请求类型数量
    '''
    from app.extensions.logger.models import Log
    from app.utils import local
    a_week_ago = local.localdate().shift(weeks=-1)
    results = Log.objects(created__gte=a_week_ago,
                          module__nin=['static', 'admin', 'unknown'])\
        .item_frequencies('method')

    methods = {
        'GET': '#61affe',
        'POST': '#49cc90',
        'DELETE': '#f93e3e',
        'PATCH': '#50e3c2',
        'PUT': '#fca130',
        'OPTIONS': '#ebebeb'
    }
    colors = []

    for k, _ in results.items():
        if k in methods:
            results[k] = int(results[k])
            colors.append(methods[k])

    data = [
        {'label': k, 'value': v}
        for k, v in results.items()
    ]

    return {
        'labels': [i['label'] for i in data],
        'values': [i['value'] for i in data],
        'colors': colors
    }

def count_last_week_dayli_tasks():
    '''
    获取上周的每日任务数量
    '''
    from flask_babel import get_timezone
    from app.extensions.celerybackend.models import Tasks
    from app.utils import local

    project = {
        "$project": {
            "cdate": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$time_start",
                    "timezone": str(get_timezone())
                }
            },
            "day": {
                "$dayOfYear": {
                    "timezone": str(get_timezone()),
                    "date": "$time_start"
                }
            }
        }
    }
    group = {
        "$group": {
            "_id": "$day",
            "date": {
                "$first": "$cdate"
            },
            "cnt": {
                "$sum": 1
            }
        }
    }
    sort = {
        "$sort": {
            '_id': 1
        }
    }
    a_week_ago = local.localdate().shift(weeks=-1)
    cursor = Tasks.objects(time_start__gte=a_week_ago).aggregate(project, group, sort)

    data = [i for i in cursor]
    labels = [i['date'] for i in data]
    cnts = [i['cnt'] for i in data]

    return {'labels': labels, 'cnts': cnts}
