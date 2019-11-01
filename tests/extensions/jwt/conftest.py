#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
import toml


@pytest.fixture(scope='session')
def db_name():
    return os.environ.get('APP_TEST_DB', 'flask_test_db')


@pytest.fixture(scope='session')
def postgresql_db_user():
    return os.environ.get('APP_TEST_DB_USER', 'postgres')


@pytest.fixture(scope='session')
def postgresql_dsn(postgresql_db_user, db_name):
    try:
        configuration = toml.load('app/config/testing.toml')
        return configuration['SQLALCHEMY_DATABASE_URI']
    except FileNotFoundError:
        return 'postgresql://{0}@localhost/{1}'.format(postgresql_db_user,
                                                       db_name)


@pytest.fixture(scope='session')
def app(postgresql_dsn):
    from flask import Flask
    from app.extensions import db, babel
    app = Flask('Test')
    app.config['SQLALCHEMY_DATABASE_URI'] = postgresql_dsn
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Shanghai'
    app.config['JWT_SECRET_KEY'] = '11'
    db.init_app(app)
    babel.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.commit()
        db.drop_all()


@pytest.fixture(scope='session')
def db(app):
    from app.extensions import db as db_module

    yield db_module
