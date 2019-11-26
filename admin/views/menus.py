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

from .bases import AuthModelView


class MenuModelView(AuthModelView):
    """菜单管理"""

    column_editable_list = AuthModelView.column_editable_list + ["name", "icon", "path"]
    column_searchable_list = ["name"]
    column_exclude_list = ["pid", "permission_id"]
    form_excluded_columns = AuthModelView.form_excluded_columns + column_exclude_list
    column_filters = AuthModelView.column_searchable_list + ["parent.name"]

    column_labels = {"parent_name": "父菜单名称", "parent": "父级菜单"}

    form_args = {"parent_name": {"allow_blank": True}}
    form_widget_args = {"children": {"disabled": True}}

    def on_model_change(self, form, model, is_created):
        """
        更新子类型数据
        """
        from app.utils.db import ClosureTable
        from app import db

        super().on_model_change(form, model, is_created)
        cl_table = ClosureTable(model)
        state = db.inspect(model)
        # 软删除
        if state.attrs.deleted.history.has_changes() and model.deleted:
            cl_table.delete_subtree()
            return
        # 创建
        if is_created:
            cl_table.insert_node()
        else:
            cl_table.move_tree()

    def on_model_delete(self, model):
        """
        删除子节点
        """
        from app.utils.db import ClosureTable

        cl_table = ClosureTable(model)
        cl_table.delete_subtree(soft_delete=False)
