# encoding: utf-8
"""
安装依赖相关的Invoke模块
"""
import logging

from invoke import task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task
def install_python_dependencies(context, force=False):
    """
    安装python依赖
    """
    log.info("安装项目依赖...")
    context.run("poetry %s" % ('upgrade' if force else 'install'), pty=True)
    log.info("项目依赖安装完毕.")


@task
def install(context):
    # pylint: disable=unused-argument
    """
    安装项目依赖
    """
    install_python_dependencies(context)
