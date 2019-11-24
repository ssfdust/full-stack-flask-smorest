#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.socketio.session
    ~~~~~~~~~~~~~~~~~~~~~

    session处理模块
"""

from flask_jwt_extended import decode_token
from flask_jwt_extended.utils import verify_token_not_blacklisted
from flask_jwt_extended.exceptions import RevokedTokenError
from jwt.exceptions import DecodeError
from app.extensions.rpcstore import AMQPStore
from app.utils.secure import encrypt_str


class SessionManager(AMQPStore):
    """
    session管理

    利用RabbitMQ来存储userid
    提供检测删除与开始功能
    """

    def __init__(self, user_hash=None):
        self.user_hash = user_hash
        self.active = False
        self.init_queue()

    def init_queue(self):
        """初始化队列"""
        if self.user_hash:
            self.active = True
            super().__init__(
                f'session_{self.user_hash}',
                exchange='session',
                expires=3600 * 24,
                limit=1,
                max_length=1,
                routing_key=self.user_hash,
                auto_delete=True)

    def check_token(self, token):
        """检测token是否存在"""
        try:
            decoded_token = decode_token(token)
            verify_token_not_blacklisted(decoded_token, 'access')
            email = decoded_token['identity']
            self.user_hash = encrypt_str(email)
            return True
        except RevokedTokenError:
            return False
        except DecodeError:
            return False

    def start_session(self):
        """开始一个session"""
        self.check_active()
        self.value = "active"
        self.save()

    def check_session(self):
        """测试一个session"""
        self.check_active()
        self.reload(requeue=True)
        return bool(self.value)

    def check_active(self):
        if self.active is False:
            self.init_queue()

    def end_session(self):
        """终结一个session"""
        self.check_active()
        self.reload()
