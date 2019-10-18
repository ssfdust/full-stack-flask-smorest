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

from flask import send_file
from flask.views import MethodView
from loguru import logger

from app.extensions.marshal.bases import BaseMsgSchema
from app.modules.auth.decorators import doc_login_required

from . import blp, models, params
from .decorators import upload_handler


@blp.route('/token_based/<int:file_id>')
class StoragesTokenBasedView(MethodView):

    @doc_login_required
    @blp.response(code=200, description='获取文件')
    def get(self, file_id):
        '''
        获取文件
        '''
        storage = models.Storages.get_by_id(file_id)

        return send_file(storage.store.stream,
                         attachment_filename=storage.name,
                         mimetype=storage.store.content_type,
                         as_attachment=False)

    @upload_handler
    @doc_login_required
    @blp.arguments(params.UploadParams(), location='files')
    @blp.response(BaseMsgSchema)
    def put(self, args, file_id):
        '''
        修改文件
        '''
        args['_store'] = args.pop('file')
        extra_args = args.pop('extra_args')
        logger.info(extra_args)
        storage = models.Storages.get_by_id(file_id)
        logger.info(f"修改了文件{storage.name} id: {storage.id}")
        storage.update(**args)

        return {'code': 0, 'msg': 'success'}

    @doc_login_required
    @blp.response(BaseMsgSchema)
    def delete(self, file_id):
        '''
        删除文件
        '''
        storage = models.Storages.get_by_id(file_id)
        logger.info(f"删除了文件{storage.name} id: {storage.id}")
        storage.delete()

        return {'code': 0, 'msg': 'success'}

@blp.route('/token_based/upload')
class UploadTokenBasedView(MethodView):

    @upload_handler
    @doc_login_required
    @blp.arguments(params.UploadParams(), location='files')
    @blp.response(BaseMsgSchema)
    def post(self, args):
        '''
        上传文件
        '''
        logger.info(f"上传了文件{args['name']}")
        args['_store'] = args.pop('file')
        extra_args = args.pop('extra_args')
        logger.info(extra_args)
        storage = models.Storages.create(**args)

        return {'code': 0, 'msg': 'success',
                'file_id': storage.id}
