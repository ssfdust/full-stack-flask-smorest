#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试ModelConverter"""


class TestModelConverter():

    def test_model_converter(self, app):
        from app.extensions.sqla.types import ArrowType
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer
        from app.extensions.marshal.ma import Marshmallow
        from app.extensions.marshal.fields import ArrowField
        from app.extensions.marshal.converters import ModelConverter

        Base = declarative_base()

        ma = Marshmallow(app)

        class SomeClass(Base):
            __tablename__ = 'some_table'

            id = Column(Integer, primary_key=True)
            time = Column(ArrowType)

        class SomeSchema(ma.ModelSchema):

            class Meta:
                model = SomeClass

        schema = SomeSchema()

        assert isinstance(schema.fields['time'], ArrowField)
        assert schema.Meta.model_converter == ModelConverter
