#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue

import pytest
from app.backtasks.send_mail import send_mail

SENDED = queue.Queue()


def fake_send(msg):
    SENDED.put(msg)


@pytest.fixture
def patched_mail(monkeypatch):
    from app.extensions import mail

    monkeypatch.setattr(mail, "send", fake_send)


class TestSendMail:
    @pytest.mark.parametrize(
        "content, template, result",
        [
            (
                {"message": "这是一个测试", "url": "testing-default"},
                "default",
                '<p>这是一个测试</p><a href="testing-default" target="_blank">点击访问</a>',
            ),
            (
                {"message": "这是一个测试", "url": "testing-reset-password"},
                "reset-password",
                '<p>这是一个测试</p><a href="testing-reset-password" target="_blank">点击访问</a>',
            ),
            (
                {"message": "这是一个测试", "url": "testing-confirm"},
                "confirm",
                '<p>这是一个测试</p><a href="testing-confirm" target="_blank">点击访问</a>',
            ),
        ],
    )
    def test_send_mail(
        self,
        flask_app,
        flask_celery_app,
        flask_celery_worker,
        patched_mail,
        content,
        template,
        result,
    ):
        req = send_mail.delay("test", "test", content, template)
        req.get(timeout=1)
        msg = SENDED.get()
        assert msg.html == result
