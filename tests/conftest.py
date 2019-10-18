#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope='session')
def flask_app():
    import os
    os.environ['FLASK_ENV'] = 'testing'

    from app.app import app, db

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
