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
    app.backtasks.send_mail
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    发送邮件模块
"""

from time import sleep

from loguru import logger
from flask_mail import Message
from flask import render_template_string

from app.extensions import celery_ext as celery
from app.extensions.celeryprogress import ProgressRecorder
from app.extensions import mail
from app.modules.email_templates.models import EmailTemplate


@celery.task(
    bind=True,
    name='发送邮件',
    max_retries=5,
    autoretry_for=(Exception,),
    acks_late=True,
    time_limit=60)
def send_mail(self, to, subject, content, template='default'):
    '''
    发送邮件

    :param          to: str                         收件人
    :param          subject: str                    主题
    :param          content: Union(dict, str)       内容
    :param          template: str                   模板
    '''
    logger.info(f'发送邮件至{to}')

    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(20, 100)
    msg = Message(subject, recipients=[to])
    template_str = EmailTemplate.get_template(template)
    msg.html = render_template_string(template_str, **content)
    progress_recorder.set_progress(80, 100)

    mail.send(msg)
    progress_recorder.set_progress(100, 100)

    sleep(1)

    return {'code': 0, 'result': 'success'}
