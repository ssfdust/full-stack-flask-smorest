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
    app.extensions.celery
    ~~~~~~~~~~~~~~~~~~~~~~

    celery模块
"""

import celery

from celery.signals import task_postrun, task_prerun, worker_process_init
from kombu import serialization
from bson import json_util


def encoder(obj):
    return json_util.dumps(obj)


def decoder(s):
    return json_util.loads(s)


def register_serializer():
    serialization.register(
        "bson",
        encoder=encoder,
        decoder=decoder,
        content_type="application/json",
        content_encoding="utf-8",
    )


# https://github.com/getsentry/zeus/blob/97528038a0abfd6f0e300d8d3f276e1b0818c328/zeus/utils/celery.py#L10


class Celery(object):

    def __init__(self, app=None):
        # we create the celery immediately as otherwise NOTHING WORKS
        self.app = None
        self.context = None
        self.celery = celery.Celery(__name__)
        if app:
            self.init_app(app)
        register_serializer()

    def init_app(self, app):
        self.app = app
        self.app_ctx = app.app_context()
        self.req_ctx = app.test_request_context()
        new_celery = celery.Celery(
            app.import_name,
            broker=app.config["CELERY_BROKER_URL"],
            backend=app.config["CELERY_RESULT_BACKEND"],
            enable_utc=True,
            timezone=app.config['BABEL_DEFAULT_TIMEZONE'])
        # XXX(dcramer): why the hell am I wasting time trying to make Celery work?
        self.celery.__dict__.update(vars(new_celery))
        self.celery.conf.update(app.config)
        self.celery.conf['BROKER_HEARTBEAT'] = 0

        worker_process_init.connect(self._worker_process_init)

        task_postrun.connect(self._task_postrun)
        task_prerun.connect(self._task_prerun)

    def task(self, *args, **kwargs):
        return self.celery.task(*args, **kwargs)

    def get_celery_app(self):
        return self.celery

    def _worker_process_init(self, **kwargs):
        self.app.app_context().push()  # pragma: no cover

    def _task_prerun(self, task, **kwargs):
        if self.app is None:
            return  # pragma: no cover

        self.app_ctx.push()
        self.req_ctx.push()

    def _task_postrun(self, task, **kwargs):
        if self.app is None:
            return  # pragma: no cover

        self.app_ctx.pop()
        self.req_ctx.pop()


celery_ext = Celery()
