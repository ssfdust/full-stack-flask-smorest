#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TestTask:
    def test_task(self, flask_app_client):
        flask_app_client.connect("/tasks")
        flask_app_client.emit("refresh_tasks", namespace="/tasks")
        data = flask_app_client.get_received("/tasks")
        assert data[0]
        flask_app_client.disconnect("/tasks")
