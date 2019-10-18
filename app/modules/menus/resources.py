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

from flask.views import MethodView
from app.modules.auth.decorators import doc_login_required
from flask_jwt_extended import current_user

from . import models
from . import blp
from . import schemas

@blp.route('')
class MenuView(MethodView):

    @doc_login_required
    @blp.response(schemas.MenuViewSchema, description='用户信息')
    def get(self):
        """
        获取用户自己的菜单
        """
        from app.utils.db import hierarchy_to_json

        permissions = [item.id for item in current_user.abilities]
        items = models.Menu.query.filter(models.Menu.permission_id.in_(permissions)).all()
        dict_items = schemas.MenuSchema(many=True).dump(items)
        data = hierarchy_to_json(dict_items)

        return {'data': data,
                'code': 0,
                'msg': 'success'}
