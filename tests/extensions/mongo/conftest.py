#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import mongoengine
import os


@pytest.fixture
def db_name():
    return os.environ.get('TEST_MONGO_DATABASE', 'test_mongo_db')


@pytest.fixture
def connection(db_name):
    try:
        conn = mongoengine.get_connection()
    except mongoengine.connection.MongoEngineConnectionError:
        try:
            import toml

            config = toml.load('app/config/testing.toml')['MONGODB_SETTINGS']

            conn = mongoengine.connect(**config)
        except FileNotFoundError:
            conn = mongoengine.connect(db_name)
    yield conn
    conn_db = mongoengine.get_db()
    conn.drop_database(conn_db.name)


@pytest.fixture
def database(connection):
    return mongoengine.get_db()
