#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import mongoengine
import os


@pytest.fixture(scope="package")
def db_name():
    return os.environ.get("TEST_MONGO_DATABASE", "test_mongo_db")


@pytest.fixture(scope="package")
def config(db_name):
    try:
        import toml

        config = toml.load("app/config/testing.toml")["MONGODB_SETTINGS"]

        return config
    except FileNotFoundError:
        return {"db": db_name}


@pytest.fixture(scope="package")
def connection(config):
    try:
        conn = mongoengine.get_connection()
    except mongoengine.connection.MongoEngineConnectionError:
        conn = mongoengine.connect(**config)
    yield conn
    conn_db = mongoengine.get_db()
    conn.drop_database(conn_db.name)


@pytest.fixture(scope="package")
def database(connection):
    return mongoengine.get_db()


@pytest.fixture(scope="package")
def app(config):
    from flask import Flask
    from app.extensions import mongo, babel, Logger

    app = Flask("TestLogger")
    app.config["MONGODB_SETTINGS"] = config
    app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
    mongo.init_app(app)
    babel.init_app(app)
    Logger(app)

    with app.app_context() as f:
        print(f)
        yield app


@pytest.fixture(scope="package")
def db(app):
    from app.extensions import mongo as db_module

    yield db_module
