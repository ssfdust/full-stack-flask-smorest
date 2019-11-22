#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app
from app.extensions.jwt.uitls import add_token_to_database
from flask_jwt_extended import create_access_token
from app.socketio.session import SessionManager


class TestSession():

    @staticmethod
    def create_token(db, regular_user):
        access_token = create_access_token(identity=regular_user.email)
        add_token_to_database(access_token, current_app.config['JWT_IDENTITY_CLAIM'])

        db.session.commit()

        return access_token

    def test_session(self, flask_app, db, regular_user):
        token = self.create_token(db, regular_user)
        session = SessionManager()
        session.check_token(token)

        assert session.check_session() is False
        session.start_session()
        for _ in range(10):
            assert session.check_session() is True
        new_session = SessionManager(session.user_hash)
        new_session.end_session()
        assert session.check_session() is False

    def test_raise(self, flask_app, db):
        session = SessionManager()
        assert session.check_token('12121212') is False
        fake_sess = SessionManager('121212')
        fake_sess.check_session() is False
