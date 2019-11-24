"""测试API"""


class TestApi():

    def test_api(self):
        from flask import Flask
        from flask.views import MethodView
        from app.extensions.api import Api
        from app.extensions.api.decorators import paginate
        from app.extensions import db, babel
        from app.extensions.sqla import SurrogatePK, Model
        import marshmallow as ma
        from flask_smorest import Blueprint
        from app.extensions.marshal.bases import BasePageSchema

        app = Flask("TestApi")
        app.config["OPENAPI_VERSION"] = "3.0.2"
        app.config["BABEL_DEFAULT_TIMEZONE"] = "Asia/Shanghai"
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

        api = Api(app)
        babel.init_app(app)
        db.init_app(app)

        class TestPagination(SurrogatePK, Model):

            name = db.Column(db.String(10))

        with app.app_context():
            TestPagination.__table__.create(db.get_engine())

        class TestSchema(ma.Schema):
            id = ma.fields.Int(dump_only=True)
            name = ma.fields.String()

        class TestPageSchema(BasePageSchema):

            data = ma.fields.List(ma.fields.Nested(TestSchema))

        blp = Blueprint('tests', 'tests')

        @blp.route('/')
        class Pets(MethodView):

            @blp.response(TestPageSchema)
            @paginate()
            def get(self, **kwargs):
                """List pets"""
                return TestPagination.query.order_by(TestPagination.id)

        api.register_blueprint(blp)

        with app.app_context():
            db.create_all()

            data = [TestPagination(name=str(i + 1)) for i in range(20)]
            db.session.bulk_save_objects(data)
            db.session.commit()

        test_client = app.test_client()
        resp = test_client.get('/?page=2&per_page=5')

        data = resp.json

        assert data['meta'] == {
            'links': {
                'first': '/?page=1&per_page=5',
                'last': '/?page=4&per_page=5',
                'next': '/?page=3&per_page=5',
                'prev': '/?page=1&per_page=5'
            },
            'page': 2, 'pages': 4,
            'per_page': 5, 'total': 20
        }
