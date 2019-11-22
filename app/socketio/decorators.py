#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.socketio.decorators
    ~~~~~~~~~~~~~~~~~~~~~~~

    socketio的验证装饰器模块
"""


from .session import SessionManager
from functools import wraps
from flask_socketio import disconnect
from flask import request


def auth_socket(func):
    """
    验证socketio的连接是否合法

    通过md5加密的连接来连接
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_id = request.args.get("user_id", None)
        if user_id is None:
            disconnect(sid=request.sid)
        else:
            session = SessionManager(user_id)
            status = session.check_session()
            if not status:
                disconnect(request.sid)

        return func(*args, **kwargs)

    return decorated_function
