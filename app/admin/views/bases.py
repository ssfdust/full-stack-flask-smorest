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
Admin模块的基础验证ORM

包含一个处理SQLA的ORM验证模块，以及
一个处理MONGOENGINE的ORM验证模块
"""
from itertools import chain

import mongoengine
from flask import abort, redirect, request, url_for
from flask_admin.contrib import mongoengine as mong
from flask_admin.contrib import sqla
from flask_security import current_user

from app.extensions.admin.converter import (
    LocalModelConverter, LocalMongoConverter
)
from app.extensions.admin.filters import MongoFilterConverter
from app.extensions.admin.typefmt import MONG_FORMATTERS, SQLA_FORMATTERS
from app.extensions.mongo import fields

# 拓展Flask-Admin的排序模块
# 以支持Mongodb的Arrow类型
# 排序
SORTABLE_FIELDS = {
    mongoengine.StringField,
    mongoengine.IntField,
    mongoengine.FloatField,
    mongoengine.BooleanField,
    mongoengine.DateTimeField,
    mongoengine.ComplexDateTimeField,
    mongoengine.ObjectIdField,
    mongoengine.DecimalField,
    mongoengine.ReferenceField,
    mongoengine.EmailField,
    mongoengine.UUIDField,
    mongoengine.URLField,
    fields.ArrowField
}


class AuthMongView(mong.ModelView):
    """
    Mongodb的ORM验证模块
    """

    page_size = 10

    model_form_converter = LocalMongoConverter

    filter_converter = MongoFilterConverter()

    column_type_formatters = MONG_FORMATTERS

    form_excluded_columns = ['created']

    edit_modal = True

    create_modal = True

    details_modal = True

    def scaffold_sortable_columns(self):
        """
        获取可以排序类型
        """
        columns = {}

        for n, f in self._get_model_fields():
            if type(f) in SORTABLE_FIELDS:
                if self.column_display_pk or not isinstance(f, mongoengine.ObjectIdField):
                    columns[n] = f

        return columns

    def get_column_name(self, field):
        """
        自定义获取栏目名称
        """
        model_labels = {
            k: c.__dict__.get('verbose_name', '')
            for k, c in self.model._fields.items()
        }
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        elif field in model_labels:
            return model_labels[field]
        else:
            return self._prettify_name(field)

    def scaffold_form(self):
        """
            Create form from the model.
        """
        model_args = {
            k: {'label': c.__dict__.get('verbose_name', '')}
            for k, c in self.model._fields.items()
        }
        model_args.update(self.form_args if self.form_args else {})
        form_class = mong.form.get_form(self.model,
                                        self.model_form_converter(self),
                                        base_class=self.form_base_class,
                                        only=self.form_columns,
                                        exclude=self.form_excluded_columns,
                                        field_args=model_args,
                                        extra_fields=self.form_extra_fields)

        return form_class

    def is_accessible(self):
        """只有SuperUser角色可以访问"""
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('SuperUser')
                )

    def _handle_view(self, name, **kwargs):
        """
        修改默认的_handle_view来添加验证
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class AuthModelView(sqla.ModelView):
    """
    SQLAlchemy的ORM验证模块
    """

    page_size = 10

    model_form_converter = LocalModelConverter

    column_filters = ['created', 'modified', 'deleted']

    form_excluded_columns = ['created', 'modified', 'deleted']

    column_editable_list = ['deleted']

    column_searchable_list = ['id', 'name']

    column_type_formatters = SQLA_FORMATTERS

    edit_modal = True

    create_modal = True

    def scaffold_list_columns(self):
        """
        将modified, deleted, created移到最后
        """
        columns = super().scaffold_list_columns()
        extra_cols = ['deleted', 'created', 'modified']
        for col in extra_cols:
            try:
                columns.append(columns.pop(columns.index(col)))
            except ValueError:
                pass

        return columns

    def get_column_name(self, field):
        """
        自定义获取栏目名称
        """
        model_labels = {
            str(k): c.doc
            for k, c in chain(
                self.model.__mapper__.columns.items(),
                self.model.__mapper__.relationships.items()
            ) if hasattr(c, 'doc') and c.doc is not None
        }
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        elif field in model_labels:
            return model_labels[field]
        else:
            return self._prettify_name(field)

    def scaffold_form(self):
        """
        根据doc自动自动定义栏目名称
        """
        model_args = {
            str(k): {'label': c.doc}
            for k, c in chain(
                self.model.__mapper__.columns.items(),
                self.model.__mapper__.relationships.items()
            ) if hasattr(c, 'doc') and c.doc is not None
        }
        model_args.update(self.form_args if self.form_args else {})
        converter = self.model_form_converter(self.session, self)
        form_class = sqla.form.get_form(self.model, converter,
                                        base_class=self.form_base_class,
                                        only=self.form_columns,
                                        exclude=self.form_excluded_columns,
                                        field_args=model_args,
                                        ignore_hidden=self.ignore_hidden,
                                        extra_fields=self.form_extra_fields)

        if self.inline_models:
            form_class = self.scaffold_inline_form_models(form_class)

        return form_class

    def is_accessible(self):
        """只有SuperUser角色可以访问"""
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('SuperUser')
                )

    def _handle_view(self, name, **kwargs):
        """
        修改默认的_handle_view来添加验证
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    def on_model_change(self, form, model, is_created):
        """
        更新修改时间
        """
        from app.utils.local import localnow
        if not is_created:
            model.modified = localnow()
