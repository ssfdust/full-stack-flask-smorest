#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试mixin模块"""

import pytest
from app.extensions.sqla.mixin import CRUDMixin, CharsTooLong, DuplicateEntry
from app.extensions.sqla.types import ArrowType
from app.utils.local import localnow
from marshmallow import Schema, fields
import copy


class TestSqlaCRUD(object):

    def test_create(self, app, db, monkeypatch):

        class SimpleCreate(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            num = db.Column(db.Integer)
            deleted = db.Column(db.Boolean, default=False)
            modified = db.Column(ArrowType(True), default=localnow)
            created = db.Column(ArrowType(True), default=localnow)

        engine = db.get_engine()
        SimpleCreate.__table__.create(engine)

        simple = SimpleCreate.create(num=1)
        assert simple.id is not None
        simple2 = SimpleCreate(num=2)
        simple2.save()
        modtime = copy.copy(simple2.modified)
        assert simple2.id is not None
        simple2.save()
        assert simple2.modified > modtime

    def test_update(self, app, db):

        class SimpleUpdate(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            num = db.Column(db.Integer)
            name = db.Column(db.String(12), default='123')
            deleted = db.Column(db.Boolean, default=False)
            modified = db.Column(ArrowType(True), default=localnow)
            created = db.Column(ArrowType(True), default=localnow)
            time = db.Column(ArrowType(True), default=localnow)

        engine = db.get_engine()
        SimpleUpdate.__table__.create(engine)

        simple = SimpleUpdate.create(num=1)
        modtime = copy.copy(simple.modified)
        assert simple.num == 1
        simple.update(
            id=10000,
            num=2,
            name='456',
            deleted=True,
            created='2008-04-12',
            time='2008-04-12',
            modified='2008-04-12')
        assert simple.num == 2
        assert simple.name == '456'
        assert simple.id != 10000
        assert simple.deleted is False
        assert simple.modified.format('YYYY-MM-DD') != '2008-04-12'
        assert simple.created.format('YYYY-MM-DD') != '2008-04-12'
        assert simple.time.format('YYYY-MM-DD') == '2008-04-12'
        assert simple.modified > modtime

    def test_delete(self, app, db):

        class SimpleDelete(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            num = db.Column(db.Integer)
            deleted = db.Column(db.Boolean, default=False)

        engine = db.get_engine()
        SimpleDelete.__table__.create(engine)
        simple = SimpleDelete.create(num=1)
        assert simple.num == 1
        assert simple.id is not None
        simple.delete()

        assert simple.deleted is True

        cnt = db.session.query(SimpleDelete).filter(
            SimpleDelete.id == simple.id).count()
        assert cnt == 1

    def test_hard_delete(self, app, db):

        class SimpleHardDelete(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            num = db.Column(db.Integer)
            deleted = db.Column(db.Boolean, default=False)

        engine = db.get_engine()
        SimpleHardDelete.__table__.create(engine)
        simple = SimpleHardDelete.create(num=1)
        assert simple.num == 1
        assert simple.id is not None
        simple.hard_delete()

        cnt = db.session.query(SimpleHardDelete).filter(
            SimpleHardDelete.id == simple.id).count()
        assert cnt == 0

    def test_update_by_ma(self, app, db):

        class TestParent(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(8))

        class TestChild(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            pid = db.Column(db.Integer, db.ForeignKey(TestParent.id))
            name = db.Column(db.String(8))
            parnet = db.relationship(
                TestParent,
                backref=db.backref('children', active_history=True),
                active_history=True)

        class ChildSchema(Schema):
            id = fields.Int()
            pid = fields.Int()
            name = fields.Str()

        class ParentSchema(Schema):
            name = fields.Str()
            children = fields.List(fields.Nested(ChildSchema))

        engine = db.get_engine()
        for t in [TestParent, TestChild]:
            t.__table__.create(engine)

        child1 = TestChild(name='1')
        child2 = TestChild(name='2')
        parent = TestParent.create(name='1', children=[child1, child2])
        modtime = copy.copy(parent.modified)
        child3 = TestChild(name='3')
        tmp_parent = TestParent(name='add1', children=[child1, child3])
        parent.update_by_ma(ParentSchema, tmp_parent, commit=False)
        assert tmp_parent.id is None
        assert parent.children == [child1, child3]
        assert parent.name == 'add1'
        new_parnet = TestParent().create()
        assert new_parnet.id == parent.id + 1
        tmp_parent = TestParent(name='add2', children=[child2, child3])
        parent.update_by_ma(ParentSchema(), tmp_parent)
        parent = db.session.query(TestParent).filter(
            TestParent.id == parent.id).one()
        assert parent.children == [child2, child3
                                  ] or parent.children == [child3, child2]
        assert parent.name == 'add2'
        new_parnet = TestParent().create()
        assert new_parnet.id == parent.id + 2
        assert parent.modified > modtime

    def test_commit(self, app, db):

        class SimpleCommit(CRUDMixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            num = db.Column(db.Integer, unique=True)
            name = db.Column(db.String(1))

        engine = db.get_engine()
        SimpleCommit.__table__.create(engine)

        SimpleCommit.create(num=1)
        with pytest.raises(DuplicateEntry):
            SimpleCommit.create(num=1)
        with pytest.raises(CharsTooLong):
            SimpleCommit.create(name='Very Long')
