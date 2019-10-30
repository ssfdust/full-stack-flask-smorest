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
存储模块

存储管理
回收站管理
"""
from flask import send_file
from flask_admin.base import expose
from flask_admin.model.template import EndpointLinkRowAction

from ..forms import JustUploadField
from .bases import AuthModelView


class StorageView(AuthModelView):
    """
    存储管理模块
    """

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    details_modal = True
    column_exclude_list = ['id', 'uid', 'path']
    form_excluded_columns = [
        'saved', 'uid', 'path', 'created', 'modified', 'deleted', 'filetype'
    ]
    column_filters = ['created', 'modified', 'storetype', 'filetype']
    form_extra_fields = {'file': JustUploadField('文件')}
    column_extra_row_actions = [
        EndpointLinkRowAction(
            icon_class='fas fa-download',
            endpoint='admin.views.storages.storage_file',
            id_arg='file_id')
    ]

    @expose('file/<int:file_id>', methods=['GET'])
    def storage_file(self, file_id):
        """访问文件"""
        storage = self.model.get_by_id(file_id)

        return send_file(
            storage.store.stream,
            attachment_filename=storage.name,
            mimetype=storage.store.content_type,
            as_attachment=False)

    def on_model_change(self, form, model, is_created):
        """保存文件处理"""
        if 'file' in form:
            model.store = form['file'].data
        if is_created:
            model.save()
        elif model.deleted is True:
            model.delete()
        else:
            # TODO 当发生更新时检查文件是否发生改变
            model.update()
        super().on_model_change(form, model, is_created)


class GarbageView(AuthModelView):

    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = False
    details_modal = False
    column_searchable_list = ['id', 'path']
    column_exclude_list = ['id', 'uid', 'path']
    column_filters = ['created', 'modified', 'storetype']

    def on_model_delete(self, model):
        """删除时删除文件"""
        model.hard_delete()
