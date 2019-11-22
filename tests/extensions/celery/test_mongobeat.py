#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.extensions.mongobeat.schedulers import MongoScheduleEntry, MongoScheduler
from app.extensions.mongobeat.models import PeriodicTask
from itertools import count
from datetime import timedelta, datetime
import pytest

_ids = count(0)


class EntryTrackSave(MongoScheduleEntry):

    def __init__(self, *args, **kwargs):
        self.save = 0
        super().__init__(*args, **kwargs)

    def sync(self):
        self.save += 1
        super().save()


class TrackingScheduler(MongoScheduler):

    Entry = EntryTrackSave

    def __init__(self, *args, **kwargs):
        self.flushed = 0
        MongoScheduler.__init__(self, *args, **kwargs)

    def sync(self):
        self.flushed += 1
        MongoScheduler.sync(self)


class SchedulerCase(object):

    def create_model_interval(self, scheduler, **kwargs):
        model = self.create_model(type="interval", **kwargs)
        model.interval = scheduler
        model.save()

        return model

    def create_model_crontab(self, scheduler, **kwargs):
        model = self.create_model(type="crontab", **kwargs)
        model.crontab = scheduler
        model.save()

        return model

    def create_model(self, **kwargs):
        entry = {
            "name": "foo{}".format(next(_ids)),
            "task": "celery.ping",
            "args": "[1, 2, 3]",
            "kwargs": '{"test": "123"}',
            "queue": "xyz",
            "routing_key": "test",
            "exchange": "foo"
        }
        return PeriodicTask(**entry, **kwargs)


class TestMongoBeat(SchedulerCase):

    Entry = EntryTrackSave

    def test_conf(app, celery_sess_app):
        assert celery_sess_app.conf.CELERY_MONGODB_SCHEDULER_COLLECTION

    def test_schedule_entry(self, app, celery_sess_app):
        schedule = PeriodicTask.Interval(every=10, period="minutes")
        interval = self.create_model_interval(schedule)
        e = self.Entry(interval)

        assert e.args == [1, 2, 3]
        assert e.kwargs == {"test": "123"}
        assert e.options["queue"] == "xyz"
        assert e.options["routing_key"] == "test"
        assert e.options["exchange"] == "foo"
        assert e.options["enabled"] is False
        assert e.schedule
        assert e.total_run_count == 0
        assert str(e._task) == "{}: every 10 minutes".format(e._task.name)

        right_now = e._default_now()
        schedule2 = PeriodicTask.Interval(every=1, period="minutes")
        m2 = self.create_model(interval=schedule2,
                               type="interval",
                               last_run_at=right_now)
        m2.save()
        e2 = self.Entry(m2)
        assert m2.interval.period_singular == "minute"
        assert str(e2._task) == "{}: every minute".format(e2._task.name)
        assert e2.last_run_at
        assert e2.total_run_count == 0
        e3 = e2.next()
        assert e3.last_run_at > e2.last_run_at
        assert e3.total_run_count == 1

    def test_entry_is_due(self, app, celery_sess_app):
        right_now = datetime.now()
        schedule = PeriodicTask.Crontab(minute="*/10")
        m = self.create_model_crontab(schedule, last_run_at=right_now,
                                      start_after=right_now + timedelta(seconds=20),
                                      max_run_count=1)
        assert str(m) == "{}: */10 * * * * (分/时/周/日/月)".format(m.name)
        e = self.Entry(m)
        is_due, next = e.is_due()
        assert is_due is False
        assert next == 5
        m.enabled = True
        m.save()
        is_due, next = e.is_due()
        assert is_due is False
        assert next == 5
        m.start_after = None
        e.total_run_count = 1
        e.last_run_at = datetime.now()
        e.sync()
        is_due, next = e.is_due()
        assert is_due is False
        assert next == 5
        m.max_run_count = 0
        m.run_immediately = True
        m.save()
        assert str(e) == "<EntryTrackSave (%s celery.ping(*[1, 2, 3], **{'test': '123'}) {5})>" % m.name
        is_due, next = e.is_due()
        assert is_due is True
        assert next != 5
        e.sync()
        is_due, next = e.is_due()
        assert is_due is False
        assert m.run_immediately is False
        assert next != 5

    def test_entry_raise(self, app, celery_sess_app):
        with pytest.raises(Exception):
            model = self.create_model()
            model.schedule
        with pytest.raises(Exception):
            model = self.create_model()
            str(model)
