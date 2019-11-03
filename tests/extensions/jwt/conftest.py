#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
import toml

import datetime

FAKE_TIME = datetime.datetime(2000, 12, 25, 17, 5, 55)


@pytest.fixture(scope='package')
def db_name():
    return os.environ.get('APP_TEST_DB', 'flask_test_db')


@pytest.fixture(scope='package')
def postgresql_db_user():
    return os.environ.get('APP_TEST_DB_USER', 'postgres')


@pytest.fixture(scope='package')
def postgresql_dsn(postgresql_db_user, db_name):
    try:
        configuration = toml.load('app/config/testing.toml')
        return configuration['SQLALCHEMY_DATABASE_URI']
    except FileNotFoundError:
        return 'postgresql://{0}@localhost/{1}'.format(postgresql_db_user,
                                                       db_name)


@pytest.fixture(scope='package')
def app(postgresql_dsn, jwt, db):
    from flask import Flask
    from app.extensions import babel
    from app.extensions.jwt.models import TokenBlackList
    from app.extensions.jwt import check_if_token_in_blacklist, token_expired, unauthorized_callback

    app = Flask('TestJwt')
    app.config['SQLALCHEMY_DATABASE_URI'] = postgresql_dsn
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Shanghai'
    app.config['JWT_SECRET_KEY'] = '11'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
    app.config['JWT_QUERY_STRING_NAME'] = 'token'
    db.init_app(app)
    babel.init_app(app)
    jwt.user_loader_callback_loader(lambda x: {"user": x})
    jwt.init_app(app)
    jwt.token_in_blacklist_loader(check_if_token_in_blacklist)
    jwt.expired_token_loader(token_expired)
    jwt.unauthorized_loader(unauthorized_callback)

    with app.app_context():
        try:
            TokenBlackList.__table__.create(db.get_engine())
        except Exception:
            pass
        db.create_all()
        yield app
        db.session.commit()


@pytest.fixture(scope='package')
def jwt():
    from app.extensions.jwt import JWTManager

    jwt_module = JWTManager()

    yield jwt_module


@pytest.fixture(scope='package')
def db():
    from app.extensions.sqla.db_instance import SQLAlchemy

    db_module = SQLAlchemy()

    yield db_module


@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

        @classmethod
        def utcnow(cls):
            return FAKE_TIME + datetime.timedelta(seconds=3600)

    monkeypatch.setattr(datetime, 'datetime', mydatetime)
