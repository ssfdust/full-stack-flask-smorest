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
    admin.extensions.admin.converter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    拓展Flask-Admin自带的转换器，以支持更多的类型
"""

from flask_admin.contrib import sqla, mongoengine
from flask_admin import form
from flask_mongoengine.wtf import orm, fields
from flask_admin.model.form import converts
from wtforms import fields as f
from flask_admin.contrib.mongoengine.subdoc import EmbeddedForm
from wtforms import validators


class LocalModelConverter(sqla.form.AdminModelConverter):
    """
    拓展sqla的转换器,默认所有指向的值都是foreign_key

    属性：
        ArrowType：Arrow对象字段，转换为时间字段

    新增ArrowType支持
    """

    def _convert_relation(self, name, prop, property_is_association_proxy, kwargs):
        """
        从flask-admin中直接复制过来
        """
        # Check if relation is specified
        form_columns = getattr(self.view, "form_columns", None)
        if form_columns and name not in form_columns:
            return None

        remote_model = prop.mapper.class_
        column = prop.local_remote_pairs[0][0]

        # 在本项目中默认不使用foreign_key

        kwargs["label"] = self._get_label(name, kwargs)
        kwargs["description"] = self._get_description(name, kwargs)

        # determine optional/required, or respect existing
        requirement_options = (validators.Optional, validators.InputRequired)
        requirement_validator_specified = any(
            isinstance(v, requirement_options) for v in kwargs["validators"]
        )
        if (
            property_is_association_proxy
            or column.nullable
            or prop.direction.name != "MANYTOONE"
        ):
            kwargs["allow_blank"] = True
            if not requirement_validator_specified:
                kwargs["validators"].append(validators.Optional())
        else:
            kwargs["allow_blank"] = False
            if not requirement_validator_specified:
                kwargs["validators"].append(validators.InputRequired())

        # Override field type if necessary
        override = self._get_field_override(prop.key)
        if override:
            return override(**kwargs)

        multiple = property_is_association_proxy or (
            prop.direction.name in ("ONETOMANY", "MANYTOMANY") and prop.uselist
        )
        return self._model_select_field(prop, multiple, remote_model, **kwargs)

    @converts("app.extensions.sqla.types.ArrowType")
    def convert_arrow_time(self, field_args, **extra):
        return form.DateTimeField(**field_args)


class CeleryBeatConverter(mongoengine.form.CustomModelConverter):
    """
    CeleryTask中的子表的转换，取消所有的验证

    属性:
        DynamicField: 动态字段，转换为JSON字段
        StringField: 字符串字段，取消required验证
        IntField: 整形字段，取消required验证

    为了在celery beat的选框中只提交一部分内容，而取消
    表单（Interval或Crontab）二选一，而表单默认验证所
    有内容。
    """

    @orm.converts("DynamicField")
    def conv_Dynamic(self, model, field, kwargs):
        return fields.JSONField(**kwargs)

    @orm.converts("StringField")
    def conv_String(self, model, field, kwargs):
        kwargs["validators"] = []
        field = super().conv_String(model, field, kwargs)
        return field

    @orm.converts("IntField")
    def conv_Int(self, model, field, kwargs):
        kwargs["validators"] = []
        field = super().conv_Int(model, field, kwargs)
        return field


class LocalMongoConverter(mongoengine.form.CustomModelConverter):
    """
    拓展Mongoengine的转换器

    属性：
        ArrowField: Arrow对象字段，转换为时间字段
        DynamicField: 动态字段，转换为Json字段

    新增ArrowField支持, DynamicField支持
    """

    @orm.converts("ArrowField")
    def conv_Arrow(self, model, field, kwargs):
        kwargs["widget"] = form.DateTimePickerWidget()
        return f.DateTimeField(**kwargs)

    @orm.converts("DynamicField")
    def conv_Dynamic(self, model, field, kwargs):
        return fields.JSONField(**kwargs)

    def clone_converter(self, view):
        """
        当Converter递归解析子ORM时，会自动
        clone自身，在此处特殊处理，如果为子项目
        则返回CeleryBeatConverter（取消子ORM校验）
        """
        if isinstance(view, EmbeddedForm):
            return CeleryBeatConverter(view)
        else:
            return self.__class__(view)
