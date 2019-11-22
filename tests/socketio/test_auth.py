#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from flask_jwt_extended import create_access_token
from app.extensions.jwt.uitls import add_token_to_database
from hashlib import md5


@pytest.mark.run(order=1)
class TestAuth():

    def test_auth(self, flask_app, flask_app_client, regular_user):
        user_hash = md5(regular_user.email.encode('utf-8')).hexdigest()
        query_string = 'user_id=' + user_hash
        access_token = create_access_token(identity=regular_user.email)
        flask_app_client.connect('/auth', query_string=query_string)
        assert flask_app_client.is_connected('/auth')

        flask_app_client.emit('authenticate', {'token': access_token},
                              namespace="/auth")
        assert flask_app_client.is_connected('/auth') is False
        add_token_to_database(access_token, flask_app.config['JWT_IDENTITY_CLAIM'])

        flask_app_client.connect('/auth', query_string=query_string)
        flask_app_client.emit('authenticate', {'token': access_token},
                              namespace="/auth")
        assert flask_app_client.is_connected('/auth')

        flask_app_client.emit('test', namespace="/auth")
        data = flask_app_client.get_received('/auth')
        assert data[0]['name']['data'] == "Hello, World"
        flask_app_client.disconnect('/auth')
        flask_app_client.connect('/auth', query_string=query_string)
        flask_app_client.emit('test', namespace="/auth")
        assert flask_app_client.is_connected('/auth') is False

        flask_app_client.connect('/auth', query_string="121212")
        assert flask_app_client.is_connected('/auth') is False
        flask_app_client.connect('/auth')
        assert flask_app_client.is_connected('/auth') is False
