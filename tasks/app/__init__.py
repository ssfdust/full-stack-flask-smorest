# encoding: utf-8
"""
Invoke的相关配置内容
"""

from invoke import Collection

from . import boilerplates, dependencies, env, run, users, celery, db

namespace = Collection(
    dependencies,
    celery,
    db,
    env,
    run,
    users,
    boilerplates,
)
