#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    app.modules.email_templates.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    电子邮件模板的ORM模块
"""

from app.extensions.sqla import Model, SurrogatePK, db


class EmailTemplate(Model, SurrogatePK):
    """
    电子邮件模板

    :attr name: str(128) 电子邮件模板名称
    """

    __tablename__ = "email_templates"

    name = db.Column(db.String(length=128), nullable=False, unique=True, doc="email_templates的名称")
    template = db.Column(db.Text, nullable=False, doc="模板")

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).one()

    @classmethod
    def get_template(cls, name):
        """获取模板"""
        template = cls.get_by_name(name)
        return template.template

    def __repr__(self):
        return self.name
