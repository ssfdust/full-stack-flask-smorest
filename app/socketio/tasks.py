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
    app.socketio.tasks
    ~~~~~~~~~~~~~~~~~~~
    任务模块的websocket模块

    主要处理进度条的实时状态
"""
from flask_socketio import Namespace, emit
from app.extensions import socketio


class TaskNamespace(Namespace):
    """
    任务用模块
    """

    def on_connect(self):
        """连接时"""

    def on_disconnect(self):
        """连接丢失时"""

    def on_refresh_tasks(self):
        """
        从队列中返回最新五个任务的进度条状态
        """
        from app.extensions.celerybackend.models import Tasks
        from app.extensions.celeryprogress import progress

        tasks = Tasks.objects(state='run').limit(5).all()
        data = [{
            'name': task.name,
            'progress': progress.get_info(str(task.id))['percent']
        } for task in tasks]

        emit('get_tasks', {'data': data})


socketio.on_namespace(TaskNamespace('/tasks'))
