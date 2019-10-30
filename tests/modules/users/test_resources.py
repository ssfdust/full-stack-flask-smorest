#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试API获取"""

import pytest


class TestUserModule():

    @pytest.mark.parametrize('data', [{"name": "test1", "description": "test"}])
    def test_group_add(self, flask_app, flask_app_client, permissions, regular_user, data):
        with flask_app_client.login(regular_user, permissions):
            resp = flask_app_client.post('/api/v1/users/groups')
            assert resp.status_code == 200

    def test_group_query(self, flask_app, flask_app_client, permissions, regular_user):
        with flask_app_client.login(regular_user, permissions):
            resp = flask_app_client.get('/api/v1/users/groups')
            assert resp.status_code == 200
