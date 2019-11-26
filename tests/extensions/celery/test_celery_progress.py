#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.extensions.celeryprogress import ProgressRecorder, progress


def test_celery_creation(celery_ext, celery_sess_app, celery_sess_worker):
    @celery_ext.task(bind=True)
    def progress_func(self):
        progress_recorder = ProgressRecorder(self)
        progress_recorder.set_progress(20, 100)

        return "test"

    celery_sess_worker.reload()

    r = progress_func.delay()

    assert r.get(timeout=1) == "test"

    with celery_ext.app.app_context():
        assert progress.get_info(str(r.id))["percent"] == 20

    for _ in range(10):
        q = progress_func.delay()

    assert q.get(timeout=1) == "test"

    with celery_ext.app.app_context():
        assert progress.get_info(str(r.id))["percent"] == 0
        assert progress.get_info(str(q.id))["percent"] == 20
