#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试MongoEngine"""


class TestMongoEngine:
    def test_ext_fields(self, app, db):

        assert hasattr(db, "ArrowField")
