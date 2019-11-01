#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_user(user):
    return {"user": user}


class TestJwt():

    def test_jwt_manager(self, app, db, monkeypatch):
        from app.extensions.jwt import jwt
        from app.extensions.jwt.uitls import add_token_to_database, revoke_token
        from app.extensions.jwt.models import TokenBlackList
        from flask_jwt_extended import create_access_token, jwt_required, current_user, get_raw_jwt
        from flask import jsonify

        jwt.user_loader_callback_loader(get_user)
        jwt.init_app(app)

        @app.route('/login', methods=['POST'])
        def login():
            token = create_access_token('test')
            add_token_to_database(token, "identity")

            return jsonify({"token": token})

        @app.route('/protected', methods=["GET"])
        @jwt_required
        def protected():
            assert current_user == {"user": "test"}
            return jsonify({"code": 1})

        @app.route('/revoke', methods=["GET"])
        @jwt_required
        def revoke():
            jwt = get_raw_jwt()
            revoke_token(jwt)
            return jsonify({"code": 1})

        test_client = app.test_client()
        resp = test_client.post("/login")
        assert resp.status_code == 200
        headers = {"Authorization": "Bearer {}".format(resp.json["token"])}
        resp = test_client.get("/protected")
        assert resp.status_code == 401
        resp = test_client.get("/protected", headers=headers)
        resp.status_code == 200

        token = TokenBlackList.query.first()
        token.expires == (1900, 1, 1, 0, 0, 0)
        token.save()
        resp = test_client.get("/protected", headers=headers)
        resp.status_code == 402

        TokenBlackList.query.delete()
        db.session.commit()
        test_client.post("/login")
        test_client.get("/revoke")
        resp = test_client.get("/protected")
        assert resp.status_code == 401
