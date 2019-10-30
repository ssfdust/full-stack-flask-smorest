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
    app.extensions.sqla.mixin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    CRUD Mixin模块

    为ORM实例添加直接增删改查的方法
    id, deleted, modified, created为系统默认字段
"""

import arrow
import psycopg2
import sqlalchemy as sa

from .db_instance import db
from .sqla import CharsTooLong, DuplicateEntry


class CRUDMixin(object):
    """CRUD基础模块(create, read, update, delete) """

    @classmethod
    def create(cls, **kwargs):
        """新建一条数据 """
        commit = kwargs.get('commit', True)
        instance = cls(**kwargs)
        return instance.save(commit)

    def update(self, commit=True, **kwargs):
        """根据特定字段更新

        更新除系统字段以外的字段，并更新修改时间
        """
        # 过滤id, deleted, modified, created字段
        kwargs.pop('id', None)
        kwargs.pop('deleted', None)
        kwargs.pop('modified', None)
        kwargs.pop('created', None)

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        # 更新修改时间
        setattr(self, 'modified', arrow.now())

        return commit and self.save() or self

    def save(self, commit=True):
        """保存对象

        保存对象并更新保存时间
        """
        setattr(self, 'modified', arrow.now())
        db.session.add(self)
        if commit:
            self.commit()
        return self

    def delete(self, commit=True):
        """软删除对象

        将数据库行的deleted字段设置为ture
        """
        self.deleted = True
        self.update(commit=commit)

    def hard_delete(self, commit=True):
        """彻底删除对象

        从数据库中彻底删除行
        """
        db.session.delete(self)
        return commit and self.commit()

    def update_by_ma(self, schema, instance, commit=True):
        """根据marshmallow以及SQLa实例更新

        :param                  schema: Schema      Schema类或实例
        :param                  instance: object    Model对象
        :param                  commit: bool        是否commit

        此方法用以更新Sqla实例的字段，基于一个marshmallow类或实例，
        根据marshmallow类的load字段加载。由于需要一个临时变量的
        instance，对于需要同时处理复杂relationship的子关系需要增
        加指定active_history=True来跟踪变化以维持正确的加载。
        形如：
        >>> class Remote(Model):
                id = Column(Integer(), primary_key=True)
                name = Column(String(80))
        >>> class Local(Model):
                id = Column(Integer(), primary_key=True)
                remote_id = Column(Integer())
                remote = relationship("Remote", active_history=True,
                            backref=backref('local', active_history=True)
                            )

        在这里需要修改Remote中name以及关系时。
        """
        from sqlalchemy.orm.attributes import get_attribute, del_attribute, set_attribute
        from marshmallow import Schema

        if not isinstance(schema, Schema):
            schema = schema()

        db.session.add(instance)

        loadable_fields = [
            k for k, v in schema.fields.items() if not v.dump_only
        ]

        with db.session.no_autoflush:
            for field in loadable_fields:
                set_attribute(self, field, get_attribute(instance, field))
                del_attribute(instance, field)

        db.session.expunge(instance)

        self.save(commit)

    def commit(self):
        """提交以及错误处理"""
        try:
            db.session.commit()
        except sa.exc.IntegrityError as e:
            if isinstance(e.orig, psycopg2.errors.UniqueViolation):
                # except psycopg2.errors.UniqueViolation:
                db.session.rollback()
                raise DuplicateEntry(str(e))
        except sa.exc.DataError as e:
            if isinstance(e.orig, psycopg2.errors.StringDataRightTruncation):
                # except psycopg2.errors.UniqueViolation:
                db.session.rollback()
                raise CharsTooLong(str(e))
