#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from app.modules.users.models import UserInfo


class TestAuthModel:
    @pytest.mark.usefixtures("flask_app", "db")
    def test_user_nickname(self, regular_user):
        regular_user.userinfo = UserInfo()
        assert regular_user.nickname == "regular_user"
        regular_user.userinfo.first_name = "李"
        assert regular_user.nickname == "regular_user"
        regular_user.userinfo.last_name = "白"
        assert regular_user.nickname == "李白"
