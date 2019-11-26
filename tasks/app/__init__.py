# encoding: utf-8
"""
Invoke的相关配置内容
"""

from invoke import Collection

from . import (
    boilerplates,
    celery,
    db,
    dependencies,
    env,
    init,
    manager,
    run,
    tests,
    users,
)

namespace = Collection(
    dependencies, celery, init, env, run, users, boilerplates, manager, tests, db,
)
