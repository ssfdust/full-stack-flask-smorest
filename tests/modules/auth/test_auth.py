#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试auth"""

import pytest
from queue import Queue
from app.backtasks.send_mail import send_mail
from app.services.auth.confirm import generate_confirm_token

MAIL_QUEUE = Queue()


@pytest.fixture
def patched_mail(monkeypatch):
    """发送邮件"""
    def fake_send(to, subject, content, template):
        print(content)
        MAIL_QUEUE.put(content["url"])
    monkeypatch.setattr(send_mail, "delay", fake_send)


class TestAuthModule():

    @pytest.mark.parametrize("captcha, code, token", [
        ('2345', 200, '1212'),
        ('1111', 403, '1212'),
        ('1111', 403, '1211'),
    ])
    def test_user_login_captcha(self, flask_app, flask_app_client,
                                regular_user, patch_code, captcha, code,
                                token):
        resp = flask_app_client.get("/api/v1/auth/captcha?token=1212")
        assert resp.status_code == 200
        login_data = {
            'email': "regular_user@email.com",
            'password': "regular_user_password",
            'token': token,
            'captcha': captcha
        }
        resp = flask_app_client.post('/api/v1/auth/login', json=login_data)
        assert resp.status_code == code

    @pytest.mark.parametrize("username, password, active, code", [
        ('test', 'test', True, 404),
        ('inactive_user@email.com', 'test', True, 403),
        ('inactive_user@email.com', 'inactive_user_password', True, 200),
        ('inactive_user@email.com', 'inactive_user_password', False, 403),
    ])
    def test_user_login_status(self, flask_app, flask_app_client, inactive_user,
                               patch_code, username, password, active, code):
        inactive_user.update(active=active)
        resp = flask_app_client.get("/api/v1/auth/captcha?token=1234")
        assert resp.status_code == 200
        login_data = {
            'email': username,
            'password': password,
            'token': '1234',
            'captcha': "2345"
        }
        resp = flask_app_client.post('/api/v1/auth/login', json=login_data)
        assert resp.status_code == code

    def test_user_confirm(self, flask_app_client, regular_user):
        regular_user.update(confirmed_at=None)
        token = generate_confirm_token(regular_user, 'confirm')
        resp = flask_app_client.get('/api/v1/auth/confirm?token={}'.format(token))
        assert resp.status_code == 200

        assert regular_user.active
        assert regular_user.confirmed_at

    @pytest.mark.parametrize("email, code", [
        ('test', 404),
        ('forget_passwd_user@email.com', 200),
    ])
    def test_user_forget_password(self, flask_app_client, patched_mail,
                                  email, code, forget_passwd_user):
        resp = flask_app_client.post('/api/v1/auth/forget-password', json={"email": email})
        forget_passwd_user.update(active=True)
        assert resp.status_code == code
        if resp.status_code == 200:
            url = MAIL_QUEUE.get(timeout=3)
            resp = flask_app_client.get(url)
            assert resp.status_code == 200
            resp = flask_app_client.put(url, json={"password": "1234567",
                                                   "confirm_password": "123456"})
            assert resp.status_code == 501
            resp = flask_app_client.put(url, json={"password": "123456",
                                                   "confirm_password": "123456"})
            assert resp.status_code == 200
            assert forget_passwd_user.verify_and_update_password('123456')
            resp = flask_app_client.get(url)
            assert resp.status_code == 401

    def test_user_refresh_token(self, flask_app_client, regular_user,
                                patch_code, flask_app):
        flask_app_client.get("/api/v1/auth/captcha?token=refresh_token")
        login_data = {
            'email': regular_user.email,
            'password': "regular_user_password",
            'token': "refresh_token",
            'captcha': '2345'
        }
        resp = flask_app_client.post('/api/v1/auth/login', json=login_data)
        refresh_token = resp.json["data"]["tokens"]['refresh_token']
        headers = {"Authorization": "Bearer {}".format(refresh_token)}
        resp = flask_app_client.post('/api/v1/auth/refresh', headers=headers)
        assert resp.status_code == 200
        access_token = resp.json["data"]['access_token']
        headers = {"Authorization": "Bearer {}".format(access_token)}
        resp = flask_app_client.post('/api/v1/auth/logout', headers=headers,
                                     json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        resp = flask_app_client.post('/api/v1/auth/logout', headers=headers,
                                     json={"refresh_token": refresh_token})
        assert resp.status_code == 401
