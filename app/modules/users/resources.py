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
from flask_jwt_extended import current_user
from loguru import logger

from app.extensions.marshal import BaseMsgSchema
from app.modules.auth import PERMISSIONS
from app.modules.auth.decorators import doc_login_required, permission_required

from . import blp, models, params, schemas


@blp.route('/groups')
class GroupView(MethodView):

    @doc_login_required
    @permission_required(PERMISSIONS.GroupQuery)
    @blp.response(schemas.GroupResSchema, description="分组信息")
    def get(self):
        """
        获取分组
        """
        from app.utils.db import hierarchy_to_json

        groups = models.Group.query.all()
        schema = schemas.GroupSchema(
            many=True, exclude=['created', 'deleted', 'modified'])
        data = schema.dump(groups)

        tree_groups = hierarchy_to_json(data)

        return {'data': tree_groups}

    @doc_login_required
    @permission_required(PERMISSIONS.GroupAdd)
    @blp.arguments(params.GroupInfoParam)
    @blp.response(BaseMsgSchema, description="分组成功")
    def post(self, group):
        """
        新增分组
        """
        from app.services.users.groups import GroupFactory

        group_factory = GroupFactory(group)
        group_factory.add_group()

        models.db.session.commit()

        logger.info(f"{current_user.email}新建了{group.name}组")

        return {'msg': 'success', 'code': 0}


@blp.route('/groups/<int:gid>')
class GroupItemView(MethodView):

    @doc_login_required
    @permission_required(PERMISSIONS.GroupQuery)
    @blp.response(schemas.GroupItemSchema, description="分组信息")
    def get(self, gid):
        """
        获取单个组信息
        """

        return {'data': models.Group.get_by_id(gid)}

    @doc_login_required
    @permission_required(PERMISSIONS.GroupEdit)
    @blp.arguments(params.GroupInfoParam)
    @blp.response(BaseMsgSchema, description="分组成功")
    def patch(self, group, gid):
        """
        修改分组
        """
        from app.services.users.groups import GroupFactory

        group = models.Group.update_by_id(gid, params.GroupInfoParam, group)

        group_factory = GroupFactory(group)
        group_factory.modify_group()

        models.db.session.commit()

        logger.info(f"{current_user.email}修改了{group.name}组")

        return {'msg': 'success', 'code': 0}

    @doc_login_required
    @permission_required(PERMISSIONS.GroupDelete)
    @blp.response(BaseMsgSchema, description="分组成功")
    def delete(self, gid):
        """
        删除分组
        """
        from app.services.users.groups import GroupFactory

        group = models.Group.get_by_id(gid)
        group_factory = GroupFactory(group)
        group_factory.delete_group()

        models.db.session.commit()

        logger.info(f"{current_user.email}删除了{group.name}组")

        return


@blp.route(
    '/groups/<int:id>/members',
    parameters=[{
        'in': 'path',
        'name': 'id',
        'description': '组ID'
    }])
class GroupMemberView(MethodView):

    @doc_login_required
    @permission_required(PERMISSIONS.GroupEdit)
    @blp.arguments(params.UserListByIdParam)
    @blp.response(BaseMsgSchema, description="修改成功")
    def put(self, users, id):
        """
        修改组成员
        """
        from app.services.users.groups import GroupFactory

        group = models.Group.get_by_id(id)
        group.users = users

        group_factory = GroupFactory(group)
        group_factory.handle_user_roles()
        logger.info(f"{current_user.email}修改了{group.name}组成员")

        models.db.session.commit()

        return {'code': 0, 'msg': 'success'}


@blp.route('/userinfo')
class UserView(MethodView):

    @doc_login_required
    @blp.response(schemas.UserDetailsSchema, description='用户信息')
    def get(self):
        """
        获取用户自己的信息
        """

        return {'data': current_user}

    @doc_login_required
    @blp.arguments(params.UserInfoParam)
    @blp.response(schemas.UserDetailsSchema, code=200, description='用户信息')
    def patch(self, userinfo):
        """
        更新用户信息
        """
        models.UserInfo.update_by_id(current_user.userinfo.id,
                                     params.UserInfoParam, userinfo)
        logger.info(f"{current_user.username}更新了个人信息")

        return {'data': current_user}
