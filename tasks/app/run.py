# encoding: utf-8
# pylint: disable=too-many-arguments
"""
运行程序相关的Invoke模块
"""

from invoke import task
import logging

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

@task(default=True)
def server(context,
           host='127.0.0.1',
           port=8000,
           pty=False,
           flask_config=None,
           use_reloader=True,
           debug=True,
           gunicorn=False,
           install_dependencies=False):
    """
    启动服务器
    """
    if install_dependencies:
        context.invoke_execute(context, 'app.dependencies.install')

    if gunicorn:
        command = f"gunicorn -b {host}:{port} -k eventlet app.app:app"
        context.run(command, pty=pty)
    else:
        command = f"python run.py -b {host} -p {port}"
        if debug:
            command += ' --debug'
        if use_reloader:
            command += ' --use-reloader'
        context.run(command, pty=pty)
