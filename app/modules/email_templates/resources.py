#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 ssfdust RedLotus
# Author: ssfdust RedLotus
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
    app.modules.email_templates.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    电子邮件模板的资源模块
"""

from flask.views import MethodView
from flask_jwt_extended import current_user
from loguru import logger

from app.extensions.api.decorators import paginate
from app.extensions.marshal.bases import BaseMsgSchema, BaseIntListSchema
from app.modules.auth import PERMISSIONS
from app.modules.auth.decorators import doc_login_required, permission_required
from app.extensions.marshal.bases import GeneralLikeArgs

from . import blp, models, params, schemas


@blp.route("/options")
class EmailTemplateListView(MethodView):
    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateQuery)
    @blp.response(schemas.EmailTemplateListSchema)
    def get(self, **kwargs):
        # pylint: disable=unused-argument
        """
        获取所有电子邮件模板选项信息
        """
        query = models.EmailTemplate.query

        items = query.all()

        return {"data": items}


@blp.route("")
class EmailTemplateView(MethodView):
    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateQuery)
    @blp.arguments(GeneralLikeArgs, location="query")
    @blp.response(schemas.EmailTemplatePageSchema)
    @paginate()
    def get(self, **kwargs):
        # pylint: disable=unused-argument
        """
        获取所有电子邮件模板信息——分页
        """
        query = models.EmailTemplate.query
        if kwargs:
            query = query.filter_like_by(**kwargs)

        return query

    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateAdd)
    @blp.arguments(params.EmailTemplateParam)
    @blp.response(schemas.EmailTemplateItemSchema)
    def post(self, email_template, **kwargs):
        # pylint: disable=unused-argument
        """
        新增电子邮件模板信息
        """
        email_template.save()
        logger.info(f"{current_user.username}新增了电子邮件模板{email_template}")

        return {"data": email_template}

    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateDelete)
    @blp.arguments(BaseIntListSchema, as_kwargs=True)
    @blp.response(BaseMsgSchema)
    def delete(self, lst, **kwargs):
        # pylint: disable=unused-argument
        """
        批量删除电子邮件模板
        -------------------------------
        :param lst: list 包含id列表的字典
        """

        models.EmailTemplate.delete_by_ids(lst["lst"])
        logger.info(f"{current_user.username}删除了电子邮件模板{lst}")


@blp.route(
    "/<int:email_template_id>",
    parameters=[{"in": "path", "name": "email_template_id", "description": "电子邮件模板id"}],
)
class EmailTemplateItemView(MethodView):
    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateEdit)
    @blp.arguments(params.EmailTemplateParam)
    @blp.response(schemas.EmailTemplateItemSchema)
    def put(self, email_template, email_template_id, **kwargs):
        # pylint: disable=unused-argument
        """
        更新电子邮件模板
        """

        email_template = models.EmailTemplate.update_by_id(
            email_template_id, params.EmailTemplateParam, email_template
        )
        logger.info(f"{current_user.username}更新了电子邮件模板{email_template.id}")

        return {"data": email_template}

    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateDelete)
    @blp.response(BaseMsgSchema)
    def delete(self, email_template_id, **kwargs):
        # pylint: disable=unused-argument
        """
        删除电子邮件模板
        """
        models.EmailTemplate.delete_by_id(email_template_id)
        logger.info(f"{current_user.username}删除了电子邮件模板{email_template_id}")

    @doc_login_required
    @permission_required(PERMISSIONS.EmailTemplateQuery)
    @blp.response(schemas.EmailTemplateItemSchema)
    def get(self, email_template_id, **kwargs):
        # pylint: disable=unused-argument
        """
        获取单条电子邮件模板
        """
        email_template = models.EmailTemplate.get_by_id(email_template_id)

        return {"data": email_template}
