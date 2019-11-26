# encoding: utf-8
"""
测试创建APP

来源：https://github.com/frol/flask-restplus-server-example/
"""
import pytest

from app.factory import CONFIG_MAPPGING, create_app, ENABLED_MODULES
from mongoengine import disconnect


def test_create_app():
    create_app(ENABLED_MODULES)


@pytest.mark.parametrize("flask_config_name", ["development", "testing"])
def test_create_app_passing_config_name(flask_config_name):
    create_app(ENABLED_MODULES, flask_config_name)
    disconnect()


@pytest.mark.parametrize("flask_config_name", ["development", "testing"])
def test_create_app_passing_FLASK_ENV_env(monkeypatch, flask_config_name):
    monkeypatch.setenv("FLASK_ENV", flask_config_name)
    create_app(ENABLED_MODULES)
    disconnect()


def test_create_app_with_non_existing_config():
    with pytest.raises(KeyError):
        create_app(ENABLED_MODULES, "non-existing-config")


def test_create_app_with_broken_config():
    CONFIG_MAPPGING["broken-import-config"] = "broken-import-config"
    with pytest.raises(FileNotFoundError):
        create_app(ENABLED_MODULES, "broken-import-config")
    del CONFIG_MAPPGING["broken-import-config"]
