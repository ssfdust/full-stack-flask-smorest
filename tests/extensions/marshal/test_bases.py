#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试基本类型"""


class TestBasesMaClass:
    def test_base_msg(self):
        from app.extensions.marshal.bases import BaseMsgSchema

        schema = BaseMsgSchema()
        data = schema.dump({})
        assert data["msg"] == "success"
        assert data["code"] == 0

    def test_base_int_list(self):
        from app.extensions.marshal.bases import BaseIntListSchema

        schema = BaseIntListSchema()
        empty = schema.load({"data": []})
        assert empty["lst"] == []
        empty = schema.load({"lst": []})
        assert empty["lst"] == []
        intlst = [1, 2, 3, 4]
        result = schema.load({"lst": intlst})
        assert result["lst"] == intlst

    def test_base_page(self):
        from app.extensions.marshal.bases import BasePageSchema

        schema = BasePageSchema()
        data = {
            "meta": {
                "page": 1,
                "per_page": 10,
                "total": 100,
                "links": {
                    "next": "nurl",
                    "prev": "purl",
                    "first": "furl",
                    "last": "lurl",
                },
            }
        }
        result = schema.dump(data)
        assert result["code"] == 0
        assert result["meta"] == data["meta"]
        assert result["msg"] == "success"
