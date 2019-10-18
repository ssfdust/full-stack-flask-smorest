# encoding: utf-8
"""
与用户相关的Invoke模块
"""

from ._utils import app_context_task

@app_context_task(help={'username': "qwe",
                        'email': "qwe@qq.com"})
def create_user(context,
                username,
                email,
                is_admin=True,
                is_active=True):
    """
    新建用户
    """
    from app.modules.auth.models import User, Role
    from app.modules.users.models import UserInfo
    from app.modules.auth import ROLES
    from app.modules.storages.models import Storages
    from flask_security.utils import encrypt_password

    password = input("Enter password: ")

    new_user = User(
        username=username,
        password=encrypt_password(password),
        email=email,
        active=is_active
    )
    if is_admin:
        su_role = Role.get_by_name(ROLES.SuperUser)
        new_user.roles.append(su_role)
        avator = Storages(name='AdminAvator.jpg',
                          storetype='avator',
                          saved=True,
                          filetype='image/jpeg',
                          path='default/AdminAvator.jpg',
                          uid=1,
                          )
    else:
        role = Role.get_by_name(ROLES.User)
        new_user.roles.append(role)
        avator = Storages(name='DefaultAvator.jpg',
                          storetype='avator',
                          saved=True,
                          filetype='image/jpeg',
                          path='default/DefaultAvator.jpg',
                          uid=1,
                          )
    UserInfo(user=new_user, avator=avator).save()
