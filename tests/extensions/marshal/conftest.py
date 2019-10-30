#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


@pytest.fixture()
def app():
    from flask import Flask

    app = Flask(__name__)
    return app
