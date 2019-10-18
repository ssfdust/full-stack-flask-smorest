# encoding: utf-8
# pylint: disable=too-many-arguments
"""
运行程序相关的Invoke模块
"""

from invoke import task

@task
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
            command += ' --reloader'
        context.run(command, pty=pty)

@task
def status(context):
    """
    查询运行状态
    """
    command = "supervisorctl status"
    context.run(command)

@task
def logs(context,
         process='gunicorn'):
    """
    打印Supervord日志
    默认: gunicorn
    """
    command = f"supervisorctl fg {process}"
    context.run(command)

@task
def shutdown(context):
    """
    关闭supervord
    """
    command = "supervisorctl shutdown"
    context.run(command)

@task(default=True)
def daemon(context):
    """
    从supervord启动多服务.
    """
    from pathlib import Path
    log_path = Path('logs')
    if not log_path.exists():
        log_path.mkdir()
    command = "supervisord"
    context.run(command)
