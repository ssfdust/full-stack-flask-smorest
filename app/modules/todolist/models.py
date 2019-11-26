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
    app.modules.todolist.modules
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    待办模块的ORM模块
"""

from app.extensions.sqla import db, Model, SurrogatePK


class TodoItem(SurrogatePK, Model):
    """
    待办表

    :attr message: str(60) 待办内容
    :attr due: DateTime 过期时间
    :attr sort: int 序号
    :attr state: bool 完成状态
    """

    __tablename__ = "todolist_items"

    def set_sort(self):
        """
        返回最新的序列数
        """
        table = self.compiled.statement.table
        sort = db.session.query(db.func.max(table.c.id) + 1).first()[0]
        return sort if sort else 1

    message = db.Column(
        db.String(60),
        doc="待办内容",
        info={"marshmallow": {"required": True, "allow_none": False}},
    )
    due = db.Column(
        db.ArrowType,
        doc="过期时间",
        info={
            "marshmallow": {
                "required": True,
                "allow_none": False,
                "format": "%Y-%m-%d %H:%M:%S",
            }
        },
    )
    sort = db.Column(db.Integer, doc="序号", default=set_sort)
    state = db.Column(db.Boolean, doc="完成状态", default=False)

    def __repr__(self):  # pragma: nocover
        return self.message
