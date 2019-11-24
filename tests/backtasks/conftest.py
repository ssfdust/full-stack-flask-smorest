#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from celery.contrib.testing.app import setup_default_app
from celery.contrib.testing import worker


@pytest.fixture(scope="package")
def flask_celery(flask_app):
    from app.extensions.celery import Celery
    celery_ext = Celery(flask_app)

    return celery_ext


@pytest.fixture(scope='package')
def flask_celery_app(flask_celery):
    test_app = flask_celery.get_celery_app()
    test_app.loader.import_task_module('celery.contrib.testing.tasks')
    with setup_default_app(test_app):
        test_app.set_default()
        test_app.set_current()
        yield test_app


@pytest.fixture(scope='package')
def flask_celery_worker(flask_celery_app):
    with worker.start_worker(flask_celery_app,
                             pool='solo',
                             perform_ping_check=False,
                             ) as w:
        yield w
