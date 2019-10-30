#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


@pytest.fixture
def permissions():
    from app.modules.auth.permissions import PERMISSIONS

    return [PERMISSIONS.UserEdit, PERMISSIONS.GroupQuery,
            PERMISSIONS.GroupAdd]
