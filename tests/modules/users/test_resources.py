#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试API获取"""

import pytest

class TestUserModule:

    @pytest.mark.parametrize(
        "group1, group2, group3", [
            (
                {
                    "name": "group1",
                    "pid": None,
                },
                {
                    "name": "group2",
                    "pid": None,
                },
                {
                    "name": "group3",
                    "pid": None,
                },
            )
        ]
    )
    def test_group_modify(
        self, flask_app_client, permissions, regular_user,
        group1, group2, group3, role1, role2, role3,
        user1, user2, user3
    ):
        with flask_app_client.login(regular_user, permissions=permissions):
            group1["roles"] = [role1.id, role2.id]
            group1["users"] = [user1.id]
            resp = flask_app_client.post("/api/v1/users/groups", json=group1)
            assert resp.status_code == 200
            assert resp.json["data"]["roles"] == group1["roles"]
            assert role1 in user1.roles

            group2["roles"] = [role2.id, role3.id]
            group2["pid"] = resp.json["data"]["id"]
            group2["users"] = [user2.id]
            resp = flask_app_client.post("/api/v1/users/groups", json=group2)
            assert resp.status_code == 200

            group3["roles"] = [role3.id]
            group3["pid"] = resp.json["data"]["id"]
            group3["users"] = [user3.id]
            resp = flask_app_client.post("/api/v1/users/groups", json=group3)
            assert resp.status_code == 200

            resp = flask_app_client.get("/api/v1/users/groups")
            assert resp.json["data"][0]["name"] == "group1"
            assert resp.json["data"][0]["children"][0]["name"] == "group2"

            group2["pid"] = None
            group2["description"] = "test"
            group2["users"] = []
            grp2_id = resp.json["data"][0]["children"][0]["id"]
            resp = flask_app_client.patch("/api/v1/users/group/{}".format(grp2_id),
                                          json=group2)
            assert resp.status_code == 200
            assert role2 not in user2.roles

            resp = flask_app_client.get("/api/v1/users/groups")
            assert len(resp.json["data"]) == 2

            resp = flask_app_client.delete("/api/v1/users/group/{}".format(resp.json["data"][0]["id"]))
            assert resp.status_code == 200
            assert user1.roles == []
            assert user2.roles == []
            assert user3.roles == [role3]
            group2["pid"] = None
            group2["users"] = [user2.id, user3.id]
            group2["roles"] = [role1.id, role2.id]
            resp = flask_app_client.patch("/api/v1/users/group/{}".format(grp2_id),
                                          json=group2)
            assert user3.roles == [role1, role2, role3]
            assert user2.roles == [role1, role2]

    def test_unauthoried_user(
        self, flask_app_client, regular_user
    ):
        with flask_app_client.login(regular_user):
            resp = flask_app_client.get("/api/v1/users/groups")
            assert resp.status_code == 403


    def test_group_query(self, flask_app_client, permissions, regular_user):
        with flask_app_client.login(regular_user, permissions=permissions):
            resp = flask_app_client.get("/api/v1/users/groups")
            assert resp.status_code == 200

    def test_guest_user_nouserinfo(
        self, flask_app_client, regular_user
    ):
        with flask_app_client.login(regular_user):
            resp = flask_app_client.get("/api/v1/users/userinfo")
            assert resp.status_code == 403

    def test_userinfo(
        self, flask_app_client, regular_user
    ):
        with flask_app_client.login(regular_user, roles=["User"]):
            resp = flask_app_client.get("/api/v1/users/userinfo")
            assert resp.status_code == 200
