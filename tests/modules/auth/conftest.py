#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from app.extensions.rpcstore.captcha import CaptchaStore


@pytest.fixture
def patch_code(monkeypatch):
    """为编码补丁"""

    def fake_code(self, length):
        self.value = '2345'
    monkeypatch.setattr(CaptchaStore, '_generate_captcha', fake_code)
    store = CaptchaStore('1111')
    store.generate_captcha()
    assert store.value == '2345'


@pytest.fixture
def permissions():
    from app.modules.auth.permissions import PERMISSIONS

    return [PERMISSIONS.UserEdit, PERMISSIONS.GroupQuery,
            PERMISSIONS.GroupAdd]
