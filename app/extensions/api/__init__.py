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


from flask_smorest import Api as BaseApi
from app.extensions.marshal import UploadField


class Api(BaseApi):

    def register_blueprint(self, blp, base_prefix=None, **options):
        """注册蓝图

        组合新前缀url与蓝图默认前缀url

        :param base_prefix str: 新的前缀
        :param blp Blueprint: 待注册蓝图
        :param options dict: 蓝图参数

        app初始化后调用
        """
        url_prefix = options.get('url_prefix', blp.url_prefix)
        if base_prefix is not None:
            options['url_prefix'] = base_prefix + url_prefix

        self._app.register_blueprint(blp, **options)

        # Register views in API documentation for this resource
        blp.register_views_in_doc(self._app, self.spec)

        # Add tag relative to this resource to the global tag list
        self.spec.tag({'name': blp.name, 'description': blp.description})


spec_kwargs = {
    'components': {
        'securitySchemes': {
            'api_key': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            },
            'refresh_key': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        }
    }
}

api = Api(spec_kwargs=spec_kwargs)

api.register_field(UploadField, 'string', 'binary')
