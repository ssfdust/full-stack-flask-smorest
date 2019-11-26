#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试自定义ma的创建"""


class TestMaCreataion:
    def test_init_app(self, app):
        from app.extensions.marshal import ma
        from marshmallow import EXCLUDE

        ma.init_app(app)

        class TestSchema(ma.Schema):

            pass

        assert TestSchema.Meta.unknown == EXCLUDE
