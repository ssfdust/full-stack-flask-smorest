import json
from collections import OrderedDict
from contextlib import contextmanager

from flask import Response
from flask.testing import FlaskClient
from werkzeug.utils import cached_property
from flask_socketio import SocketIOTestClient


class AuthSocketIOClient(SocketIOTestClient):

    def __getattr__(self, name):
        if hasattr(self.flask_test_client, name):
            return getattr(self.flask_test_client, name)

        raise AttributeError


class JSONResponse(Response):
    """
    A Response class with extra useful helpers, i.e. ``.json`` property.

    来源：https://github.com/frol/flask-restplus-server-example/
    """

    # pylint: disable=too-many-ancestors

    @cached_property
    def json(self):
        return json.loads(self.get_data(as_text=True), object_pairs_hook=OrderedDict)


class AutoAuthFlaskClient(FlaskClient):
    """
    A helper FlaskClient class with a useful for testing ``login`` context
    manager.
    """

    def __init__(self, *args, **kwargs):
        super(AutoAuthFlaskClient, self).__init__(*args, **kwargs)
        self._user = None
        self._role = None
        self._roles = None
        self._permissions = None

    @contextmanager
    def login(self, user, roles=None, permissions=None):
        """
        示例：
            >>> with flask_app_client.login(user, permissions=['SuperUserPrivilege']):
            ...     flask_app_client.get('/api/v1/users/')
        """
        self._user = user
        self._roles = roles or []
        self._permissions = permissions or []
        yield self
        self._user = None
        self._role = None
        self._roles = None
        self._permissions = None

    def _set_user_test_role(self):
        from app.modules.auth.models import Role, db
        for role in self._user.roles:
            if role.name == "test_role":
                break
        else:
            role = Role.get_by_name("test_role")
            if not role:
                role = Role(name="test_role")
            self._user.roles.append(role)
            self._user.save(False)
        self._role = role

        role_names = [role.name for role in self._user.roles]
        for role in self._roles:
            if role not in role_names:
                self._user.roles.append(Role(name=role))
                self._user.save(False)
        db.session.flush()

    def _set_user_test_permissions(self):
        from app.modules.auth.models import Permission, db
        for permission in self._permissions:
            if permission not in [p.name for p in self._user.permissions]:
                self._role.permissions.append(Permission(name=permission))
        db.session.flush()

    def open(self, *args, **kwargs):
        from app.extensions import db
        from app.modules.auth.models import Role, Permission
        from flask_jwt_extended import create_access_token
        from flask import current_app
        from app.extensions.jwt.uitls import add_token_to_database
        if self._user is not None:
            self._set_user_test_role()

            self._set_user_test_permissions()

            access_token = create_access_token(identity=self._user.email)
            add_token_to_database(
                access_token, current_app.config["JWT_IDENTITY_CLAIM"]
            )

            db.session.commit()

            extra_headers = (
                ("Authorization", "Bearer {token}".format(token=access_token)),
            )
            if kwargs.get("headers"):
                kwargs["headers"] += extra_headers
            else:
                kwargs["headers"] = extra_headers

        response = super(AutoAuthFlaskClient, self).open(*args, **kwargs)

        if self._user:
            self._role.permissions = []
            self._user.roles = []
            db.session.flush()
            stmt = Permission.__table__.delete().where(Permission.name.in_(self._permissions))
            db.session.execute(stmt)
            stmt = Role.__table__.delete().where(Role.name.in_(self._roles))
            self._role.hard_delete()
            db.session.execute(stmt)
            db.session.commit()

        return response


def generate_user_instance(
    user_id=None, username="username", password=None, email=None, is_active=True,
):
    """
    Returns:
        user_instance (User) - an not committed to DB instance of a User model.
    """
    from app.modules.auth.models import User
    from flask_security.utils import encrypt_password

    if password is None:
        password = encrypt_password("%s_password" % username)
    user_instance = User(
        id=user_id,
        active=is_active,
        username=username,
        email=email or "%s@email.com" % username,
        password=password,
    )
    return user_instance
