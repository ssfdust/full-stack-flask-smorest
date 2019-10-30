# encoding: utf-8
# pylint: disable=invalid-name,unused-argument,too-many-arguments
"""
数据库操作相关Invoke模块

Forked from frol/flask-restplus-server-example
"""
import argparse
import logging
import os

from ._utils import app_context_task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

try:
    from alembic import __version__ as __alembic_version__
    from alembic.config import Config as AlembicConfig
    from alembic import command
except ImportError:
    log.warning(
        "Alembic cannot be imported, so some app.db.* tasks won't be available!"
    )
else:

    alembic_version = tuple(
        [int(v) for v in __alembic_version__.split('.')[0:3]])

    class Config(AlembicConfig):
        """
        自定义配置
        """

        def get_template_directory(self):
            package_dir = os.path.abspath(os.path.dirname(__file__))
            return os.path.join(package_dir, 'db_templates')


def _get_config(directory, x_arg=None, opts=None):
    """
    预准备AlembicConfig实例
    """
    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    if config.cmd_opts is None:
        config.cmd_opts = argparse.Namespace()
    for opt in opts or []:
        setattr(config.cmd_opts, opt, True)
    if x_arg is not None:
        if not getattr(config.cmd_opts, 'x', None):
            setattr(config.cmd_opts, 'x', [x_arg])
        else:
            config.cmd_opts.x.append(x_arg)
    return config


@app_context_task(
    help={
        'directory': "迁移脚本目录",
        'multidb': "迁移复数个数据库",
    })
def init(context, directory='migrations', multidb=False):
    """初始化迁移脚本"""
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    if multidb:
        command.init(config, directory, 'flask-multidb')
    else:
        command.init(config, directory, 'flask')


@app_context_task(
    help={
        'rev_id':
            "手动指定revision id",
        'version_path':
            "Specify specific path from config for version file",
        'branch_label':
            "Specify a branch label to apply to the new revision",
        'splice':
            "Allow a non-head revision as the 'head' to splice onto",
        'head':
            "Specify head revision or <branchname>@head to base new revision on",
        'sql':
            "显示待执行的Sql语句",
        'autogenerate':
            "自动对比Model，并根据历史版本生成迁移脚本",
        'directory':
            "迁移脚本目录",
    })
def revision(context,
             directory='migrations',
             message=None,
             autogenerate=False,
             sql=False,
             head='head',
             splice=False,
             branch_label=None,
             version_path=None,
             rev_id=None):
    """生成新的迁移脚本"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.revision(
            config,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id)
    else:
        command.revision(config, message, autogenerate=autogenerate, sql=sql)


@app_context_task(
    help={
        'rev_id':
            "手动指定revision id",
        'version_path':
            "Specify specific path from config for version file",
        'branch_label':
            "Specify a branch label to apply to the new revision",
        'splice':
            "Allow a non-head revision as the 'head' to splice onto",
        'head':
            "Specify head revision or <branchname>@head to base new revision on",
        'sql':
            "显示待执行的Sql语句",
        'directory':
            "迁移脚本目录",
    })
def migrate(context,
            directory='migrations',
            message=None,
            sql=False,
            head='head',
            splice=False,
            branch_label=None,
            version_path=None,
            rev_id=None):
    """'revision --autogenerate'的简写"""
    config = _get_config(directory, opts=['autogenerate'])
    if alembic_version >= (0, 7, 0):
        command.revision(
            config,
            message,
            autogenerate=True,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id)
    else:
        command.revision(config, message, autogenerate=True, sql=sql)


@app_context_task(help={
    'revision': "revision标志",
    'directory': "迁移脚本目录",
})
def edit(context, revision='current', directory='migrations'):
    """编辑一个迁移脚本"""
    if alembic_version >= (0, 8, 0):
        config = _get_config(directory)
        command.edit(config, revision)
    else:
        raise RuntimeError('Alembic 0.8.0 or greater is required')


@app_context_task(
    help={
        'rev_id': "设置revision id",
        'branch_label': "设置分支标签",
        'message': "one or more revisions, or 'heads' for all heads",
        'directory': "迁移脚本目录",
    })
def merge(context,
          directory='migrations',
          revisions='',
          message=None,
          branch_label=None,
          rev_id=None):
    """在两个迁移版本的基础上新建新的迁移版本"""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.merge(
            config,
            revisions,
            message=message,
            branch_label=branch_label,
            rev_id=rev_id)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@app_context_task(
    help={
        'tag': "Arbitrary 'tag' name - can be used by custom env.py scripts",
        'sql': "显示待执行的Sql语句",
        'revision': "revision标志",
        'directory': "迁移脚本目录",
        'x_arg': "经由自定义env.py脚本处理的额外参数",
    })
def upgrade(context,
            directory='migrations',
            revision='head',
            sql=False,
            tag=None,
            x_arg=None,
            app=None):
    """更新下一个数据库版本"""
    config = _get_config(directory, x_arg=x_arg)
    command.upgrade(config, revision, sql=sql, tag=tag)


@app_context_task(
    help={
        'tag': "Arbitrary 'tag' name - can be used by custom env.py scripts",
        'sql': "显示待执行的Sql语句",
        'revision': "revision标志",
        'directory': "迁移脚本目录",
        'x_arg': "经由自定义env.py脚本处理的额外参数",
    })
def downgrade(context,
              directory='migrations',
              revision='-1',
              sql=False,
              tag=None,
              x_arg=None):
    """回退到上一个数据哭版本"""
    config = _get_config(directory, x_arg=x_arg)
    if sql and revision == '-1':
        revision = 'head:-1'
    command.downgrade(config, revision, sql=sql, tag=tag)


@app_context_task(help={
    'revision': "revision标志",
    'directory': "迁移脚本目录",
})
def show(context, directory='migrations', revision='head'):
    """显示详情信息"""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.show(config, revision)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@app_context_task(
    help={
        'verbose': "显示详情信息",
        'rev_range': "Specify a revision range; format is [start]:[end]",
        'directory': "迁移脚本目录",
    })
def history(context, directory='migrations', rev_range=None, verbose=False):
    """显示历史"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.history(config, rev_range, verbose=verbose)
    else:
        command.history(config, rev_range)


@app_context_task(
    help={
        'resolve_dependencies': "Treat dependency versions as down revisions",
        'verbose': "显示详情信息",
        'directory': "迁移脚本目录",
    })
def heads(context,
          directory='migrations',
          verbose=False,
          resolve_dependencies=False):
    """新"""
    if alembic_version >= (0, 7, 0):
        config = _get_config(directory)
        command.heads(
            config, verbose=verbose, resolve_dependencies=resolve_dependencies)
    else:
        raise RuntimeError('Alembic 0.7.0 or greater is required')


@app_context_task(
    help={
        'verbose': "显示详情",
        'directory': "迁移脚本目录",
    })
def branches(context, directory='migrations', verbose=False):
    """显示当前分支信息"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.branches(config, verbose=verbose)
    else:
        command.branches(config)


@app_context_task(
    help={
        'verbose': "显示详情信息",
        'directory': "迁移脚本目录",
    })
def current(context, directory='migrations', verbose=False, head_only=False):
    """显示各个数据库的版本"""
    config = _get_config(directory)
    if alembic_version >= (0, 7, 0):
        command.current(config, verbose=verbose, head_only=head_only)
    else:
        command.current(config)


@app_context_task(
    help={
        'tag': "Arbitrary 'tag' name - can be used by custom env.py scripts",
        'sql': "显示待执行的Sql语句",
        'revision': "revision标志",
        'directory': "迁移脚本目录",
    })
def stamp(context, directory='migrations', revision='head', sql=False,
          tag=None):
    """
    'stamp' the revision table with the given revision
    """
    config = _get_config(directory)
    command.stamp(config, revision, sql=sql, tag=tag)
