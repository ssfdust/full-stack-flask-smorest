#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import marshmallow


class TestCustomFields:
    @pytest.mark.parametrize(
        "time", ["2019-09-01", "2019-09-01 09:00:10", "2019-09-01T09:00:10.008Z"]
    )
    def test_arrow_field(self, app, time):
        import arrow

        from app.extensions.marshal.ma import Marshmallow
        from app.extensions.marshal.fields import ArrowField

        ma = Marshmallow(app)

        class TestSchema(ma.Schema):

            time = ArrowField()

        test_data = {"time": time}

        schema = TestSchema()
        instance = schema.load(test_data)

        assert instance["time"] == arrow.get(test_data["time"])

    def test_validate(self, app):
        from app.extensions.marshal.ma import Marshmallow
        from app.extensions.marshal.fields import ArrowField

        ma = Marshmallow(app)

        class TestSchema(ma.Schema):

            time = ArrowField()

        test_data = {"time": ""}
        schema = TestSchema()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load(test_data)
