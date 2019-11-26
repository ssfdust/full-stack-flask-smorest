# encoding: utf-8
# pylint: disable=too-many-arguments
"""
supervisord相关的Invoke模块
"""

from invoke import task
import logging

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task
def status(context):
    """
    查询运行状态
    """
    command = "supervisorctl status"
    context.run(command)


@task(help={"program": "supervisord.conf中定义的program名"})
def start(context, program):
    """
    运行服务
    """
    command = f"supervisorctl start {program}"
    context.run(command)


@task(help={"program": "supervisord.conf中定义的program名"})
def stop(context, program):
    """
    停止服务
    """
    command = f"supervisorctl stop {program}"
    context.run(command)


@task(help={"program": "supervisord.conf中定义的program名"})
def restart(context, program):
    """
    重启服务
    """
    command = f"supervisorctl restart {program}"
    context.run(command)


@task(help={"program": "supervisord.conf中定义的program名"})
def logs(context, program="gunicorn"):
    """
    打印Supervord日志
    默认: gunicorn
    """
    command = f"supervisorctl fg {program}"
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

    log_path = Path("logs")
    if not log_path.exists():
        log_path.mkdir()
    command = "supervisord"
    context.run(command)
