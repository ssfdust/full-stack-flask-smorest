#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2019 RedLotus <ssfdust@gmail.com>
# Author: RedLotus <ssfdust@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    app.modules.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    用户验证的API资源模块
"""

from flask import abort, send_file
from flask import current_app as app
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token, create_refresh_token, decode_token, get_jwt_identity,
    get_raw_jwt
)
from loguru import logger

from app.extensions.jwt.uitls import add_token_to_database, revoke_token
from app.extensions.marshal import BaseMsgSchema
from app.utils import local

from . import blp, models, params, schemas
from .decorators import doc_refresh_required, doc_login_required


@blp.route('/login')
class LoginView(MethodView):

    @blp.arguments(params.LoginParams, location='json')
    @blp.response(code=407, description="用户未激活")
    @blp.response(code=408, description="验证码失效")
    @blp.response(code=409, description="验证码错误")
    @blp.response(code=404, description="用户不存在")
    @blp.response(code=403, description="用户密码错误")
    @blp.response(schemas.UserViewPostSchema, description='登录成功')
    def post(self, args):
        '''
        用户登录

        用户名密码登录后，返回基本信息以及token，
        登录方式为token方式
        '''
        from app.extensions.rpcstore.captcha import CaptchaStore
        from amqp.exceptions import NotFound

        try:
            store = CaptchaStore(args['token'])
            code_lst = store.get_captcha()
            if args['captcha'] not in code_lst:
                abort(409, "验证码错误")
        except NotFound:
            abort(408, "验证码失效")

        user = models.User.get_by_email(args['email'])

        if user is None:
            logger.warning(f"{args['email']} 不存在")
            abort(404, "用户不存在")

        if user.active is not True:
            logger.warning(f"{args['email']} 未激活，尝试登录")
            abort(407, "用户未激活")

        if user.verify_and_update_password(args['password']) is True:

            # 生成jwt
            access_token = create_access_token(identity=args['email'])
            refresh_token = create_refresh_token(identity=args['email'])

            # 将token加入数据库
            add_token_to_database(access_token, app.config['JWT_IDENTITY_CLAIM'])
            add_token_to_database(refresh_token, app.config['JWT_IDENTITY_CLAIM'])

            logger.info(f"{args['email']} 登录成功")

            # 组装data
            data = {
                'tokens': {
                    'refresh_token': refresh_token,
                    'access_token': access_token
                }
            }
            return {'code': 0, 'msg': 'success',
                    'data': data}
        else:
            logger.error(f"{args['email']} 登录密码错误")
            abort(403, "密码错误")


@blp.route('/captcha')
class CaptchaView(MethodView):

    @blp.arguments(params.CaptchaParam, location='query', as_kwargs=True)
    @blp.response(code=200, description='图片')
    def get(self, token):
        '''
        获取验证码图片

        每次随机生成一个token来获取图片，延时时间为5分钟
        '''
        from app.extensions.rpcstore.captcha import CaptchaStore
        from captcha.image import ImageCaptcha

        image = ImageCaptcha()
        store = CaptchaStore(token)
        code = store.generate_captcha()
        data = image.generate(code)

        return send_file(data, attachment_filename='captcha.jpeg')


@blp.route('/forget-password')
class ForgetPasswordView(MethodView):

    @blp.arguments(params.EmailParam, as_kwargs=True)
    @blp.response(code=404, description='用户不存在')
    @blp.response(BaseMsgSchema, description='成功')
    def post(self, email):
        '''
        忘记密码

        发送忘记密码邮件到请求的email
        '''
        from app.services.auth.confirm import generate_confirm_token
        from app.backtasks.send_mail import send_mail

        user = models.User.get_by_email(email)
        if user:
            logger.info(f"{user.email}发起了忘记密码申请")
            token = generate_confirm_token(user, 'passwd')
            send_mail.delay(user.email, '找回密码', {'token': token}, 'emails/reset-password.html')
        else:
            abort(404, "用户不存在")

        return {'code': 0,
                'msg': 'success'}


@blp.route('/confirm')
class UserConfirmView(MethodView):

    @doc_login_required
    @blp.arguments(params.JwtParam, location='query')
    @blp.response(BaseMsgSchema, description='验证成功')
    def get(self, args):
        '''
        完成用户验证
        '''
        from app.services.auth.confirm import confirm_token

        jti = get_raw_jwt()['jti']
        _, user = confirm_token(jti, 'confirm')
        logger.info(f"{user.email}完成了用户验证")
        user.update(confirmed_at=local.localnow(),
                    active=True)

        return {'code': 0,
                'msg': 'success'}


@blp.route('/reset-forgot-password')
class ResetForgotPasswordView(MethodView):

    @doc_login_required
    @blp.arguments(params.PasswdParam, as_kwargs=True)
    @blp.response(code=501, description='密码不一致，修改失败')
    @blp.response(BaseMsgSchema, description='验证成功')
    def put(self, password, confirm_password):
        '''
        忘记密码后修改

        根据token设置密码
        -------------------------------
        :param              password: str               原密码
        :param              confirm_password: str       确认密码
        '''
        from app.services.auth.confirm import confirm_token
        from flask_security.utils import encrypt_password

        jti = get_raw_jwt()['jti']
        _, user = confirm_token(jti, 'passwd')
        if password == confirm_password:
            logger.info(f"{user.email} 修改了密码")
            user.update(password=encrypt_password(confirm_password))

            return {'code': 0,
                    'msg': 'success'}
        else:
            logger.error(f"{user.email} 密码提交错误")
            abort(501, "密码不一致，修改失败")

    @doc_login_required
    @blp.response(code=403, description='禁止访问')
    @blp.response(BaseMsgSchema, description='可以访问')
    def get(self):
        '''
        忘记密码token测试

        测试token是否可用
        '''
        from app.services.auth.confirm import check_confirm_token

        jti = get_raw_jwt()['jti']
        state, _ = check_confirm_token(jti, 'passwd')

        if state:
            return {'code': 0,
                    'msg': 'success'}
        else:
            abort(403, "禁止访问")


@blp.route('/refresh')
class RefreshJwtTokenView(MethodView):

    @blp.response(schemas.RefreshViewPostSchema, description='获取成功')
    @doc_refresh_required
    def post(self):
        '''
        用户刷新Token

        用户用refresh_token获取新的token
        '''
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        logger.info(f"{current_user} 刷新了token")
        add_token_to_database(access_token, app.config['JWT_IDENTITY_CLAIM'])

        return {'code': 0, 'msg': 'success',
                'data': {'access_token': access_token}}


@blp.route('/logout')
class LogoutView(MethodView):

    @blp.arguments(schemas.RefreshTokenSchema(only=['refresh_token']),
                   as_kwargs=True)
    @blp.response(BaseMsgSchema, description='登出成功')
    @doc_login_required
    def post(self, refresh_token):
        '''
        用户登出

        带着token并以refresh_token为参数访问此api，即可完成登出，token失效
        '''
        # 清空access_token, refresh_token
        access_token = get_raw_jwt()
        refresh_token = decode_token(refresh_token, allow_expired=True)

        logger.info(f"{access_token['identity']}撤销了{access_token['jti']}")
        logger.info(f"{refresh_token['identity']}撤销了{refresh_token['jti']}")
        logger.info(f"{refresh_token['identity']}已登出")

        for raw_jwt in [access_token, refresh_token]:
            revoke_token(raw_jwt)

        return {'code': 0, 'msg': 'success'}
