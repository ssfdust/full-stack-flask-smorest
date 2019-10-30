#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""测试验证码"""


import pytest


class TestCapture():

    @pytest.mark.parametrize("key", [
        ("test1"),
        ("test2"),
        ("test3"),
        ("test4"),
        ("test6"),
    ])
    def test_save_restore_capture(self, flask_app, key):
        from app.extensions.rpcstore.captcha import CaptchaStore

        store = CaptchaStore(key)
        store.generate_captcha()
        value = store.value[:]
        store = CaptchaStore(key)
        store.get_captcha()

        assert store.value == value
