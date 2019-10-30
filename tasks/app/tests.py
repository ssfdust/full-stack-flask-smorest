# encoding: utf-8
# pylint: disable=invalid-name,unused-argument,too-many-arguments
"""
单元测试相关的Invoke模块
"""
import logging

from invoke import task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task(
    default=True,
    help={
        'directory': '单元测试目录',
        'with-cov': 'pytest-cov支持 （默认：否）',
        'cov': 'cov检测目录(当启用pytest-cov时必填)',
        'with-pdb': '开启pdb支持 （默认：否）'
    })
def tests(context, directory='tests', with_cov=False, cov='', with_pdb=False):
    """
    对项目进行单元测试
    """
    import pytest
    command = [directory, '-v']
    if with_cov and not cov:
        log.critical("pytest-cov已开启但是缺少cov参数")
        return
    elif with_cov and cov:
        command.extend(['--cov-report', 'term-missing', '--cov', cov])
    if with_pdb:
        command.extend(['--pdb'])
    exit_code = pytest.main(command)
    return exit_code
