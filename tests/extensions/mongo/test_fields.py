#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试MongoEngine自定义类型"""

import pytest
import mongoengine as db
from app.extensions.mongo.fields import ArrowField
import arrow


def faketimezone():
    return "Asia/Shanghai"


class TestArrowField():
    """测试ArrowField"""

    def test_arrow_from_empty_string(self, database):
        class Sample(db.Document):
            created = ArrowField()

        with pytest.raises(db.errors.ValidationError):
            md = Sample(created="")
            md.save()

    def test_arrow_from_whitespace_string(self, database):
        class Sample(db.Document):
            created = ArrowField()
        with pytest.raises(Exception):
            md = Sample(created="    ")
            md.save()

    def test_regular_usage(self, monkeypatch):
        import flask_babel
        monkeypatch.setattr(flask_babel, "get_timezone", faketimezone)

        class Sample(db.Document):
            created = ArrowField()

        Sample.drop_collection()

        d1 = (1970, 1, 1, 0, 0, 1)
        sample = Sample()
        sample.created = d1
        sample.validate()
        sample.save()

        for i in range(1971, 1990):
            d = arrow.get(i, 1, 1, 0, 0, 1)
            Sample(created=d).save()

        assert Sample.objects.count() == 20

        # Test ordering
        samples = Sample.objects.order_by("created")
        i = 0
        while i < 19:
            assert samples[i].created <= samples[i + 1].created
            i += 1

        samples = Sample.objects.order_by("-created")
        i = 0
        while i < 19:
            assert samples[i].created >= samples[i + 1].created
            i += 1

        # Test searching
        samples = Sample.objects.filter(created__gte=arrow.get(1980, 1, 1))
        assert samples.count() == 10

        samples = Sample.objects.filter(created__lte=arrow.get(1980, 1, 1))
        assert samples.count() == 10

        samples = Sample.objects.filter(
            created__lte=arrow.get(1980, 1, 1), created__gte=arrow.get(1975, 1, 1)
        )
        assert samples.count() == 5

    def test_utc_time(self, monkeypatch):
        import flask_babel
        monkeypatch.setattr(flask_babel, "get_timezone", faketimezone)

        class Sample(db.Document):
            created = ArrowField()

        Sample.drop_collection()

        time = arrow.get('2015-01-01 09:00:00')
        sample = Sample(
            created=time
        )
        sample.save()
        time1 = arrow.get('2015-01-01 08:59:59')
        samples = Sample.objects.filter(created__gte=time1).all()
        assert len(samples) == 1
        assert samples[0].id == sample.id
        time2 = arrow.get('2015-01-01 08:59:59+08:00')
        samples = Sample.objects.filter(created__gte=time2).all()
        assert len(samples) == 1
        assert samples[0].id == sample.id