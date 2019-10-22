# encoding: utf-8
# pylint: disable=invalid-name,unused-argument,too-many-arguments
"""
数据以及初始化相关的Invoke模块
"""
import logging

from invoke import task

from ._utils import app_context_task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@task(
    help={
        'su_passwd': 'root密码',
        'config_types': '配置类型（默认：development、testing）'
    }
)
def create_pg_db_and_user(context, su_passwd=None,
                          config_types=[]):
    """
    根据配置新建postgresql数据库以及用户
    """
    import getpass

    if su_passwd is None:
        su_passwd = getpass.getpass('sudo password:')
    if len(config_types) == 0:
        config_types = ['development', 'testing']
    for config_type in config_types:
        with open(f'cmds/{config_type}_createpg.sh') as f:
            part = f.read()
        log.info(f"正在为{config_type}配置创建rdb")
        context.sudo(f"bash -c 'psql postgres <<< $(echo {part})'", user='postgres', password=su_passwd)


@task(
    help={
        'admin': '管理员账户（默认: admin）',
        'passwd': '管理员密码（默认: admin）',
        'config_types': '配置类型（默认：development、testing）'
    }
)
def create_mg_db_and_user(context, admin='admin', passwd='admin',
                          config_types=[]):
    """
    根据配置新建mongodb数据库以及用户
    """
    if len(config_types) == 0:
        config_types = ['development', 'testing']
    for config_type in config_types:
        command = f"mongo -u {admin} -p{passwd} < cmds/{config_type}_mongodb.txt"
        log.info(f"正在为{config_type}配置创建rdb")
        context.run(command, echo=True, pty=True)


@app_context_task
def add_closure_table_procedure(context):
    """
    导入闭包表所需要的存储过程
    """
    from app.app import app
    from pathlib import Path

    log.info("正在导入闭包表...")

    engine = app.extensions['sqlalchemy'].db.get_engine()
    cursor = engine.raw_connection().cursor()
    for path in Path('tasks/app/procedures').iterdir():
        with open(path) as f:
            raw = f.read()
            cursor.execute(raw)
    cursor.execute('COMMIT')
    log.info("闭包表导入成功.")


@app_context_task(
    help={'skip_on_failure': '忽略错误（默认：否）'}
)
def init_development_data(context, skip_on_failure=False):
    """
    初始化诸如用户、用户权限等基本信息到数据库
    """

    log.info("初始化应用数据...")
    add_closure_table_procedure(context)

    from migrations import initial_development_data
    try:
        initial_development_data.init()
        initial_development_data.update_permissions()
    except AssertionError as exception:
        if not skip_on_failure:
            log.error("%s", exception)
        else:
            log.debug(
                "The following error was ignored due to the `skip_on_failure` flag: %s",
                exception
            )
            log.info("Initializing development data step is skipped.")
    else:
        log.info("数据初始化成功.")


@app_context_task
def update_app_permissions(context):
    """
    更新权限
    """

    log.info("正在更新应用权限...")
    from migrations import initial_development_data

    initial_development_data.update_permissions()

    log.info("应用权限更新完毕.")


@app_context_task
def dropdb(context):
    """
    删除数据库
    """
    from app.extensions import db
    db.drop_all()


@app_context_task
def initdb(context):
    """
    初始化数据库
    """
    from app.extensions import db
    db.create_all()
