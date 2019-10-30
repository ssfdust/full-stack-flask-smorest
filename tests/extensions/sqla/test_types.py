#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sqlalchemy as sa
import arrow
from datetime import datetime
from dateutil import tz


def faketimezone():
    return 'Asia/Shanghai'


@pytest.fixture
def Sample(Base, monkeypatch):
    from app.extensions.sqla.types import ArrowType
    import flask_babel

    monkeypatch.setattr(flask_babel, "get_timezone", faketimezone)

    class Sample(Base):
        __tablename__ = 'sample'
        id = sa.Column(sa.Integer, primary_key=True)
        created_at = sa.Column(ArrowType)
        published_at = sa.Column(ArrowType(timezone=True))
        published_at_dt = sa.Column(sa.DateTime(timezone=True))

    return Sample


@pytest.fixture
def init_models(Sample):
    pass


class TestArrowDateTimeType(object):

    def test_python_type(self, session, Sample):
        from app.extensions.sqla.types import ArrowType
        assert ArrowType().python_type == datetime

    def test_parameter_processing(self, session, Sample):
        sample = Sample(created_at=datetime(2000, 11, 1))

        session.add(sample)
        session.commit()

        sample = session.query(Sample).first()
        assert sample.created_at.datetime

    def test_tuple(self, session, Sample):
        sample = Sample(created_at=(1994, 9, 11))
        session.add(sample)
        session.commit()

        sample = session.query(Sample).first()
        assert sample.created_at.format('YYYY-MM-DD') == '1994-09-11'

    def test_none(self, session, Sample):
        sample = Sample(created_at=None)
        session.add(sample)
        session.commit()

        sample = session.query(Sample).first()
        assert sample.created_at is None

    def test_string_coercion(self, session, Sample):
        sample = Sample(created_at='1367900664')
        session.add(sample)
        session.commit()
        assert sample.created_at.year == 2013

    def test_utc(self, session, Sample):
        time = arrow.utcnow()
        sample = Sample(created_at=time)
        session.add(sample)
        assert sample.created_at == time
        session.commit()
        timezone = tz.gettz(faketimezone())
        assert sample.created_at == time.replace(tzinfo=timezone)

    def test_other_tz(self, session, Sample):
        time = arrow.utcnow()
        local = time.to(faketimezone())
        sample = Sample(created_at=local)
        session.add(sample)
        assert sample.created_at == time == local
        session.commit()
        assert sample.created_at == time

    def test_literal_param(self, session, Sample):
        time = arrow.get('2015-01-01 09:00:00')
        clause = Sample.created_at > '2015-01-01 09:00:00'
        compiled = clause.compile(compile_kwargs={"literal_binds": True})
        assert str(compiled) == 'sample.created_at > 2015-01-01 01:00:00'
        clause = Sample.created_at > time
        compiled = clause.compile(compile_kwargs={"literal_binds": True})
        assert str(compiled) == 'sample.created_at > 2015-01-01 01:00:00'

        sample = Sample(created_at=time)

        session.add(sample)
        session.commit()
        time1 = arrow.get('2015-01-01 08:59:59')
        items = session.query(Sample).filter(Sample.created_at > time1).all()
        assert len(items) == 1
        assert items[0].id == sample.id

        time2 = arrow.get('2015-01-01 08:59:59+08:00')
        items = session.query(Sample).filter(Sample.created_at > time2).all()
        assert len(items) == 1
        assert items[0].id == sample.id

    def test_timezone(self, session, Sample):
        timezone = tz.gettz('Europe/Stockholm')
        dt = arrow.get(datetime(2015, 1, 1, 15, 30, 45), timezone)
        sample = Sample(published_at=dt, published_at_dt=dt.datetime)

        session.add(sample)
        session.commit()
        session.expunge_all()

        item = session.query(Sample).one()
        assert item.published_at.datetime == item.published_at_dt
        assert item.published_at.to(timezone) == dt
