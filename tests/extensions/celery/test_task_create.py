#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_celery_creation(celery_ext, celery_sess_app, celery_sess_worker):
    from flask import current_app
    from app.extensions.celerybackend.models import Tasks

    @celery_ext.task
    def mul(x, y):
        assert current_app.config is not None
        return x * y

    celery_sess_worker.reload()

    r = mul.delay(4, 4)

    assert r.get(timeout=1) == 16
    with celery_ext.app.app_context():
        assert Tasks.get_by_id_str(r.id) is not None
