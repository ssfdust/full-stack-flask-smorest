# encoding: utf-8
"""
Shell相关的Invoke模块
"""

from invoke import task


@task
def enter(context):
    """
    进入IPython的开发shell，类似于flask shell
    """
    from app import app
    from IPython.terminal.ipapp import load_default_config
    from traitlets.config.loader import Config

    import pprint
    import sys

    import flask
    import IPython
    from app.modules.users.models import UserInfo
    from app.modules.auth.models import User
    from app.extensions import db

    flask_app = app.app

    def shell_context():
        context = dict(pprint=pprint.pprint)
        context.update(vars(flask))
        context.update(vars(app))
        context["User"] = User
        context["db"] = db
        context["UserInfo"] = UserInfo
        return context

    if "IPYTHON_CONFIG" in flask_app.config:
        config = Config(flask_app.config["IPYTHON_CONFIG"])
    else:
        config = load_default_config()

    config.TerminalInteractiveShell.banner1 = """Python %s on %s
IPython: %s
App: %s [%s]
Instance: %s""" % (
        sys.version,
        sys.platform,
        IPython.__version__,
        flask_app.import_name,
        flask_app.env,
        flask_app.instance_path,
    )

    flask_app.shell_context_processors.append(shell_context)

    with flask_app.app_context():
        IPython.start_ipython(
            argv=[], user_ns=flask_app.make_shell_context(), config=config,
        )
