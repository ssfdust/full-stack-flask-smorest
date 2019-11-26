#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TestLog:
    def test_log_api(self, app, db):
        from app.extensions.logger.models import Log

        Log.drop_collection()

        @app.route("/test/api")
        def index():
            return "11"

        client = app.test_client()
        client.get("/test/api?name=1&pass=2")
        log = Log.objects.order_by("-id").first()
        assert log.method == "GET"
        assert log.status_code == 200
        assert log.url == "/test/api"
        assert log.arguments["name"] == "1"
        assert log.arguments["pass"] == "2"
        client.post("/test/api/111")
        log = Log.objects.order_by("-id").first()
        assert log.method == "POST"
        assert log.status_code == 404
        assert log.url == "/test/api/111"

        assert Log.objects.count() == 2

    def test_logger_handler(self, app, db):
        from app.extensions.logger.models import Message
        from loguru import logger

        logger.debug("test1")
        msg = Message.objects.order_by("-id").first()
        assert msg.message == "test1"
        logger.debug("test2")
        msg = Message.objects.order_by("-id").first()
        assert msg.message == "test2"
