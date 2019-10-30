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
    app.extensions.sqla
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    拓展Flask-SQLAlchemy模块

    新增软删除功能
    新增ArrowType支持
    新增对象CRUD功能

    核心部分从一个flask-restful项目中摘录出来，现在已经找不到了
"""

from .mixin import CRUDMixin
from .db_instance import db
from flask_sqlalchemy import BaseQuery

try:
    from app.utils.local import localnow
except ImportError:
    localnow = None


class QueryWithSoftDelete(BaseQuery):
    """
    软删除模块

    根据deleted字段来决定是否显示此对象
    """

    _with_deleted = False

    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(
                deleted=False) if not obj._with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(
            db.class_mapper(self._mapper_zero().class_),
            session=db.session(),
            _with_deleted=True)

    def _get(self, *args, **kwargs):
        """提供原本的get方法"""
        return super(QueryWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        # the query.get method does not like it if there is a filter clause
        # pre-loaded, so we need to implement it using a workaround
        obj = self.with_deleted()._get(*args, **kwargs)
        return obj if obj is None or self._with_deleted or not obj.deleted else None


class Model(CRUDMixin, db.Model):
    """简单的CRUD处理"""

    query_class = QueryWithSoftDelete

    __abstract__ = True


# https://speakerdeck.com/zzzeek/building-the-app


class SurrogatePK(object):
    """
    数据库表栏目模板

    :attr           id: int             主键
    :attr           deleted: bool       删除状态
    :attr           modified: Arrow     修改时间
    :attr           created: Arrow      创建时间
    """

    id = db.Column(
        db.Integer, primary_key=True, info={'marshmallow': {
            'dump_only': True
        }})
    deleted = db.Column(
        db.Boolean,
        nullable=False,
        doc='已删除',
        default=False,
        info={'marshmallow': {
            'dump_only': True
        }})
    modified = db.Column(
        db.ArrowType(True),
        nullable=False,
        doc='修改时间',
        default=localnow,
        info={
            'marshmallow': {
                'format': '%Y-%m-%d %H:%M:%S',
                'dump_only': True
            }
        })
    created = db.Column(
        db.ArrowType(True),
        nullable=False,
        doc='创建时间',
        default=localnow,
        info={
            'marshmallow': {
                'format': '%Y-%m-%d %H:%M:%S',
                'dump_only': True
            }
        })

    @classmethod
    def get_by_id(cls, id):
        """
        根据ID查询数据库
        """
        from . import db

        if any(
            (isinstance(id, str) and id.isdigit(), isinstance(id,
                                                              (int, float))),):
            with db.session.no_autoflush:
                return cls.query.get_or_404(int(id))

    @classmethod
    def delete_by_id(cls, id, commit=True):
        """
        根据ID删除数据
        """
        item = cls.get_by_id(id)
        item.delete(commit)

    @classmethod
    def delete_by_ids(cls, ids, commit=True):
        """
        批量删除
        """
        kw = [{'id': id, 'deleted': True} for id in ids]
        db.session.bulk_update_mappings(cls, kw)

        if commit:
            db.session.commit()

    @classmethod
    def update_by_id(cls, id, schema, instance, commit=True):
        """
        根据id，Schema，以及临时实例更新元素

        :param          ids: list           主键
        :param          schema: Schema      Schema类或实例
        :param          instance: object    临时Model对象
        :param          commit: bool        是否提交

        详见update_by_ma注释
        """
        item = cls.get_by_id(id)

        item.update_by_ma(schema, instance, commit=commit)

        return item
