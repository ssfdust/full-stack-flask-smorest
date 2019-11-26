#!/usr/bin/env python
# -*- coding: utf-8 -*-


def test_group_children_query(flask_app):
    from app.modules.users.models import Group, db, groups_users
    from app.modules.auth.models import Role, User
    from app.services.users.groups import GroupFactory
    from app.services.users import create_user

    r1 = Role(name="role1").save(False)
    r2 = Role(name="role2").save(False)
    r3 = Role(name="role3").save(False)

    u1 = User(username="test1", email="test1", password="123")
    u2 = User(username="test2", email="test2", password="123")
    u3 = User(username="test3", email="test3", password="123")
    for u in [u1, u2, u3]:
        create_user(u)

    grp1 = Group(name="父1", roles=[r1], users=[u1])
    grpfc1 = GroupFactory(grp1)
    grpfc1.add_group()

    grp2 = Group(name="子1-1", roles=[r2], parent=grp1, users=[u2, u3])
    grpfc2 = GroupFactory(grp2)
    grpfc2.add_group()

    grp3 = Group(name="子1-1-1", roles=[r3], parent=grp2, users=[u3, u1])
    grpfc3 = GroupFactory(grp3)
    grpfc3.add_group()
    assert grpfc3.check_soft_delete() is False

    db.session.commit()
    assert r1 in u1.roles
    assert r2 in u2.roles
    assert r2 in u3.roles
    assert r3 in u1.roles
    assert r3 in u3.roles

    grp3.deleted = True
    grpfc3 = GroupFactory(grp3)
    assert grpfc3.check_soft_delete() is True
    db.session.commit()

    grpfc1.delete_group(soft_delete=False)
    db.session.commit()

    assert r3 not in u3.roles
    assert r2 not in u2.roles
    assert r1 not in u3.roles
    db.session.rollback()
