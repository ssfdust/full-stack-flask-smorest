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


@pytest.fixture(scope='session')
def db_name():
    return os.environ.get('APP_TEST_DB', 'flask_test_db')


@pytest.fixture(scope='session')
def postgresql_db_user():
    return os.environ.get('APP_TEST_DB_USER', 'postgres')


@pytest.fixture
def postgresql_dsn(postgresql_db_user, db_name):
    try:
        configuration = toml.load('app/config/testing.toml')
        return configuration['SQLALCHEMY_DATABASE_URI']
    except FileNotFoundError:
        return 'postgresql://{0}@localhost/{1}'.format(postgresql_db_user, db_name)


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
