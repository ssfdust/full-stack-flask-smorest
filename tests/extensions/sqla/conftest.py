#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os
import toml
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions


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
def db():
    from app.extensions.sqla.sqla import SQLAlchemy

    db_module = SQLAlchemy()

    yield db_module


@pytest.fixture(scope='package')
def app(postgresql_dsn, db):
    from flask import Flask
    from app.extensions import babel
    app = Flask('TestSqla')
    app.config['SQLALCHEMY_DATABASE_URI'] = postgresql_dsn
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Shanghai'
    db.init_app(app)
    babel.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.commit()
        db.drop_all()


@pytest.fixture
def engine(postgresql_dsn):
    engine = create_engine(postgresql_dsn)
    # engine.echo = True
    return engine


@pytest.fixture
def connection(engine):
    return engine.connect()


@pytest.fixture
def Base():
    return declarative_base()


@pytest.fixture
def Sample(Base):

    class Sample(Base):
        __tablename__ = 'sample'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode(255))

    return Sample


@pytest.fixture
def init_models(Sample):
    pass


@pytest.fixture
def session(request, engine, connection, Base, init_models):
    sa.orm.configure_mappers()
    Base.metadata.create_all(connection)
    Session = sessionmaker(bind=connection)
    session = Session()

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)
        connection.close()
        engine.dispose()

    request.addfinalizer(teardown)

    return session
