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
Admin首页模块

返回首页统计信息
- 注册信息
- 访问统计信息
- 任务统计信息
- 发送邮件功能
"""
from flask import jsonify, redirect, url_for
from flask_admin import AdminIndexView as BaseAdminIndexView
from flask_admin.base import BaseView, expose
from loguru import logger


class AdminIndexView(BaseAdminIndexView):
    @expose()
    def index(self):
        """
        首页统计信息

        返回任务统计以及注册信息
        """
        from ..forms import TodoForm
        from admin.services.admin.statistics import get_main_page_info

        info, task_success, task_run, task_fail = get_main_page_info()

        form = TodoForm()
        logger.debug(info)

        return self.render(
            self._template,
            info=info,
            todoform=form,
            task_success=task_success,
            task_run=task_run,
            task_fail=task_fail,
        )


class VisitStatisticView(BaseView):
    @expose("/")
    def index(self):
        """
        API访问统计图表API
        """
        from admin.services.admin import statistics as stat

        daily_stat = stat.count_last_week_dayli_requests()
        method_stat = stat.count_last_week_method_requests()

        return jsonify({"daily_stat": daily_stat, "method_stat": method_stat})


class TasksStatisticView(BaseView):
    @expose("/")
    def index(self):
        """上周任务状态统计API"""
        from admin.services.admin import statistics as stat

        task_stat = stat.count_last_week_dayli_tasks()

        return jsonify({"task_stat": task_stat})


class IndexRedirectView(BaseView):
    @expose()
    def index(self):
        return redirect(url_for("admin.index"))


class MailSendView(BaseView):
    @expose(methods=["POST"])
    def index(self):
        """发送邮件API"""
        from flask import request
        from app.backtasks.send_mail import send_mail

        send_mail.delay(
            request.form["emailto"],
            request.form["subject"],
            {"message": request.form["content"], "url": "#"},
        )

        return jsonify({"code": 0, "msg": "success"})


class TodoListView(BaseView):
    @expose("/", methods=["PATCH"])
    def index(self):
        from flask import request
        from app.modules.todolist.schemas import TodoItemSchema
        from app.modules.todolist.models import TodoItem, db

        data = request.get_json()
        if "data" in data and isinstance(data["data"], list):
            db.session.bulk_update_mappings(TodoItem, data["data"])
            db.session.commit()
        else:
            item = TodoItemSchema(only=["id", "state"]).load(data)
            item.save()
        return {"code": 0, "msg": "success"}

    @expose("/items", methods=["GET", "POST", "DELETE"])
    def todoitems(self):
        """待办列表"""
        from flask import request
        from app.modules.todolist.models import TodoItem
        from app.modules.todolist.schemas import TodoItemSchema

        if request.method == "GET":
            pagination = TodoItem.query.order_by(TodoItem.sort.desc()).paginate()
            data = TodoItemSchema(many=True).dump(pagination.items)

            return {"code": 0, "data": data, "meta": {"total": pagination.total}}
        elif request.method == "POST":
            data = request.get_json()
            item = TodoItemSchema().load(data)
            item.save()

            return {"code": 0, "msg": "success"}
        elif request.method == "DELETE":
            data = request.get_json()
            item = TodoItem.get_by_id(data["id"])
            item.delete()

            return {"code": 0, "msg": "success"}
