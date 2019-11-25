#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_celery_creation(celery_ext, celery_sess_app, celery_sess_worker):
    from flask import current_app
    from app.extensions.celerybackend.models import Tasks

    class Test():
        a = 1

    @celery_ext.task
    def mul(x, y):
        assert current_app.config is not None
        return Test()

    @celery_ext.task
    def mulpar(x, y):
        assert current_app.config is not None
        mul.delay(4, 4)
        return Test()

    @celery_ext.task
    def mulerr(x, y):
        assert current_app.config is not None
        return {'a': Test()}

    celery_sess_worker.reload()

    mulpar.delay(4, 4).get(timeout=1)
    r = mul.delay(4, 4)

    assert 'tests.extensions.celery.test_task_create.test_celery_creation.<locals>.Test' in r.get(timeout=1)
    with celery_ext.app.app_context():
        assert Tasks.get_by_id_str(r.id) is not None

    r = mulerr.delay(4, 4)
    assert r.result is None
