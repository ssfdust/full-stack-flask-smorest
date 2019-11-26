#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from celery.contrib.testing.app import setup_default_app
from celery.contrib.testing import worker


@pytest.fixture(scope="package")
def config():
    from app.extensions.flask.config import Config

    config = Config()
    try:
        config.from_toml("app/config/testing.toml")
        config.pop("CELERY_IMPORTS", None)
    except FileNotFoundError:

        class TestConfig:
            CELERY_MONGODB_SCHEDULER_COLLECTION = "schedules"
            CELERY_RESULT_BACKEND = "app.extensions.celerybackend:MongoBackend"
            CELERY_BROKER_URL = "amqp://"
            CELERY_TASK_SERIALIZER = "bson"
            CELERY_ACCEPT_CONTENT = ["bson", "json"]
            CELERY_EVENT_SERIALIZER = "bson"
            CELERY_RESULT_SERIALIZER = "bson"
            BABEL_DEFAULT_TIMEZONE = "Asia/Shanghai"

        config.from_object(TestConfig)

    return config


@pytest.fixture(scope="package")
def app(config):
    from flask import Flask
    from app.extensions import mongo, babel

    app = Flask("TestCelery")
    config.init_app(app)
    mongo.init_app(app)
    babel.init_app(app)

    return app


@pytest.fixture(scope="package")
def celery_ext(app):
    from app.extensions.celery import Celery

    celery_ext = Celery(app)

    return celery_ext


@pytest.fixture(scope="package")
def celery_sess_app(celery_ext):
    test_app = celery_ext.get_celery_app()
    test_app.loader.import_task_module("celery.contrib.testing.tasks")
    with setup_default_app(test_app):
        test_app.set_default()
        test_app.set_current()
        yield test_app


@pytest.fixture(scope="package")
def celery_sess_worker(request, celery_sess_app):
    with worker.start_worker(
        celery_sess_app, pool="solo", perform_ping_check=False,
    ) as w:
        yield w
