"""测试API"""


class TestApi():

    def test_api_init(self):
        from flask import Flask
        from app.extensions.api import Api

        app = Flask("TestApi")
        app.config["OPENAPI_VERSION"] = "3.0.2"
        app = Api(app)
