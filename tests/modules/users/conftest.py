#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from app.modules.auth.permissions import PERMISSIONS
from app.modules.auth.models import Role
from tests import utils


@pytest.fixture
def permissions():

    return [PERMISSIONS.UserEdit, PERMISSIONS.GroupQuery, PERMISSIONS.GroupAdd,
            PERMISSIONS.GroupEdit, PERMISSIONS.GroupDelete]


@pytest.fixture
def role1(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        Role(name="role1")
    ):
        yield _


@pytest.fixture
def role2(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        Role(name="role2")
    ):
        yield _


@pytest.fixture
def role3(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        Role(name="role3")
    ):
        yield _


@pytest.fixture
def user1(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username="user1")
    ):
        yield _


@pytest.fixture
def user2(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username="user2")
    ):
        yield _


@pytest.fixture
def user3(temp_db_instance_helper):
    for _ in temp_db_instance_helper(
        utils.generate_user_instance(username="user3")
    ):
        yield _
