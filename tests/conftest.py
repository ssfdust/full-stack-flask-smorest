#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from app.extensions import socketio
from . import utils


@pytest.fixture(scope='session')
def flask_app():
    import os
    os.environ['FLASK_ENV'] = 'testing'

    from app.app import app
    from app.extensions import db
    from app.extensions.sqla.sqla import DuplicateEntry
    from migrations.initial_development_data import init_email_templates

    with app.app_context():
        db.create_all()
        try:
            init_email_templates()
        except DuplicateEntry:
            pass
        yield app
        db.session.rollback()
        db.drop_all()


@pytest.yield_fixture(scope='session')
def db(flask_app):
    from app.extensions import db as db_instance
    yield db_instance


@pytest.fixture(scope='session')
def flask_app_client(flask_app):
    flask_app.test_client_class = utils.AutoAuthFlaskClient
    flask_app.response_class = utils.JSONResponse
    test_client = flask_app.test_client()
    return utils.AuthSocketIOClient(flask_app, socketio,
                                    flask_test_client=test_client)


@pytest.fixture(scope='session')
def temp_db_instance_helper(db):
    def temp_db_instance_manager(instance):
        instance.save()

        yield instance

        mapper = instance.__class__.__mapper__
        assert len(mapper.primary_key) == 1
        if instance not in db.session:
            db.session.add(instance)
        instance.__class__.query\
            .filter(mapper.primary_key[0] == mapper.primary_key_from_instance(instance)[0])\
            .delete()

    return temp_db_instance_manager


@pytest.fixture(scope='session')
def regular_user(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username='regular_user')
    ):
        yield _


@pytest.fixture(scope='session')
def inactive_user(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username='inactive_user')
    ):
        yield _


@pytest.fixture(scope="session")
def forget_passwd_user(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username='forget_passwd_user')
    ):
        yield _
