#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import jsonify


class TestJwt:
    def test_jwt_manager(self, app, db, monkeypatch, jwt):
        from app.extensions.jwt.uitls import add_token_to_database
        from flask_jwt_extended import create_access_token, jwt_required, current_user
        from app.extensions.jwt.models import TokenBlackList

        token = create_access_token("test")
        add_token_to_database(token, "identity")

        @app.route("/protected", methods=["GET"])
        @jwt_required
        def protected():
            assert current_user == {"user": "test"}
            return jsonify({"code": 1})

        test_client = app.test_client()

        headers = {"Authorization": "Bearer {}".format(token)}
        resp = test_client.get("/protected")
        assert resp.status_code == 401
        resp = test_client.get("/protected", headers=headers)
        resp.status_code == 200

        TokenBlackList.query.delete()
        db.session.commit()

        resp = test_client.get("/protected", headers=headers)
        resp.status_code == 401

    def test_jwt_expired(self, app, db, jwt):
        from app.extensions.jwt.models import TokenBlackList
        from app.extensions.jwt.uitls import add_token_to_database
        from flask_jwt_extended import create_access_token
        from datetime import timedelta

        token = create_access_token("test", expires_delta=-timedelta(seconds=1))
        add_token_to_database(token, "identity", allow_expired=True)

        headers = {"Authorization": "Bearer {}".format(token)}
        test_client = app.test_client()

        resp = test_client.get("/protected", headers=headers)
        assert resp.status_code == 402

        TokenBlackList.query.delete()
        db.session.commit()

    def test_jwt_revoke(self, app, db, jwt):
        from app.extensions.jwt.uitls import add_token_to_database, revoke_token
        from flask_jwt_extended import create_access_token, decode_token
        from app.extensions.jwt.models import TokenBlackList

        token = create_access_token("test",)
        add_token_to_database(token, "identity", allow_expired=True)

        _jwt = decode_token(token)
        revoke_token(_jwt)
        headers = {"Authorization": "Bearer {}".format(token)}
        test_client = app.test_client()

        resp = test_client.get("/protected", headers=headers)
        assert resp.status_code == 401

        TokenBlackList.query.delete()
        db.session.commit()

        revoke_token(_jwt)
