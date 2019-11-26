# -*- coding: utf-8 -*-
"""测试自定义的Flask"""

import tempfile
import pytest

from pathlib import Path


class TestFlask:
    def test_flask(self):
        from app.extensions.flask import Flask

        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(b"TEST_CONFIG = 123")

        app = Flask("TestFlask")
        app.config.from_toml(fp.name)

        assert app is not None
        assert app.config["TEST_CONFIG"] == 123

    def test_error(self):
        from app.extensions.flask.config import Config

        config = Config()
        with pytest.raises(IOError):
            config.from_toml("Error")
        with pytest.raises(TypeError):
            config.from_mapping(("TEST", "b"), ("TESTC", "c"))

    def test_mapping(self):
        from app.extensions.flask.config import Config

        config = Config()
        config.from_mapping([("TEST", "test")])
        assert config["TEST"] == "test"

    def test_config_init(self):
        from app.extensions.flask.config import Config
        from flask import Flask

        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(b"TEST_CONFIG = 123")
        config = Config(root_path=str(Path(__name__)))
        config.from_toml(fp.name)
        app = Flask("TestConfInit")
        config.init_app(app)
        assert app.config["TEST_CONFIG"] == 123
        Config(app=app)
        assert "TEST_CONFIG" in app.config

    def test_get_namespace(self):
        from app.extensions.flask.config import Config

        config = Config()
        config.from_mapping({"TEST_A": 1, "TEST_B": 2, "EAT_C": 3})
        assert config.get_namespace("TEST_") == {"a": 1, "b": 2}
        assert config.get_namespace("TEST_", trim_namespace=False) == {
            "test_a": 1,
            "test_b": 2,
        }
