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
数据库的相关操作
"""


class ClosureTable:
    """
    闭包表的基本操作
    """

    def __init__(self, model):
        self.model = model
        self.table = model.__class__

    def insert_node(self, commit=False):
        """
        为指定的树形闭包表添加节点

        此操作将会给xx, xx_relation建立父子关系
        需要导入tasks/app/procedures中的sql，才能执行

        :param              table: Model                ORM表
        :param              id: int                     添加的节点ID
        :param              pid: int                    添加的父节点ID
        """
        from app.extensions import db

        try:
            # 处理pid
            db.session.flush()
            db.session.execute(
                "select insert_node(:table, :id, :pid)", {
                    'table': self.table.__tablename__,
                    'id': self.model.id,
                    'pid': self.model.pid
                })
        except Exception:
            db.session.rollback()
            raise Exception
        else:
            if commit:
                db.session.commit()

    def delete_subtree(self, soft_delete=True, commit=False):
        """
        为指定的树形闭包表删除节点

        !!!警告!!! 此操作会连同删除整个子树

        :param              table: Model                ORM表
        :param              id: int                     添加的节点ID
        """
        from app.extensions import db
        try:
            if soft_delete:
                db.session.execute("select soft_delete_subtree(:table, :id)", {
                    'table': self.table.__tablename__,
                    'id': self.model.id
                })
            else:
                db.session.execute("select delete_subtree(:table, :id)", {
                    'table': self.table.__tablename__,
                    'id': self.model.id
                })
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            if commit:
                db.session.commit()

    def move_tree(self, commit=False):
        """
        为指定的树形闭包表移动节点

        :param              table: Model                ORM表
        :param              id: int                     待移动的节点ID
        :param              pid: int                    新的父节点ID
        """
        from app.extensions import db

        try:
            state = db.inspect(self.model)
            if state.attrs.pid.history.has_changes(
            ) or state.attrs.parent.history.has_changes():
                db.session.flush()
                db.session.execute(
                    "select move_subtree(:table, :id, :pid)", {
                        'table': self.table.__tablename__,
                        'id': self.model.id,
                        'pid': self.model.pid
                    })
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            if commit:
                db.session.commit()

    def print_subtree(self):
        """
        打印树
        """
        from app.extensions import db
        cursor = db.session.execute(
            "select * from get_child_nodes(:table, :id)"
            " order by breadcrumbs", {
                'table': self.table.__tablename__,
                'id': self.model.id
            })
        items = cursor.fetchall()
        for item in items:
            print(item.name)
            print('|')


def hierarchy_to_json(items):
    """
    将一个树形单列表dict转为树形

    来源：https://stackoverflow.com/questions/16069840
    要求items中的每一个节点都带有pid和id两个属性

    :params                 items: list                 节点列表

    返回值是一个带有children和
    :return                 top: list                   一个树形对象
    """
    nodes = {}
    top = []

    for record in items:
        nodes[record['id']] = record
        record['children'] = []

    for record in items:
        if record['pid'] in nodes:
            nodes[record['pid']]['children'].append(record)
        else:
            top.append(record)
    return top
