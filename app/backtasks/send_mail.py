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

from loguru import logger

from app.extensions import celery_ext as celery
from app.extensions.celeryprogress import ProgressRecorder
from time import sleep

@celery.task(bind=True, name='发送邮件', max_retries=5, autoretry_for=(Exception,),
             acks_late=True, time_limit=60)
def send_mail(self, to, subject, content, template='emails/default.html'):
    '''
    发送邮件

    :param          to: str                         收件人
    :param          subject: str                    主题
    :param          content: Union(dict, str)       内容
    :param          template: str                   模板
    '''
    from flask_mail import Message
    from app.extensions import mail
    from flask import render_template

    logger.info(f'发送邮件至{to}')

    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(20, 100)
    msg = Message(subject, recipients=[to])
    msg.html = render_template(template, **content)
    progress_recorder.set_progress(80, 100)

    mail.send(msg)
    progress_recorder.set_progress(100, 100)

    sleep(1)

    return {'code': 0, 'result': 'success'}
