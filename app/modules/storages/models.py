# Copyright 2019 RedLotus <ssfdust@gmail.com>
# Author: RedLotus <ssfdust@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from app.extensions.sqla import Model, SurrogatePK, db
from app.utils import local
from uuid import uuid4
from flask import current_app
from pathlib import Path
from werkzeug.datastructures import FileStorage
from loguru import logger

import mimetypes
import os

class StoragesCRUDMixin(object):

    def save(self, commit=True):
        self.save_store()
        return super().save(commit)

    def delete(self, commit=True):
        GarbageStorages.create(path=self.path,
                               storetype=self.storetype,
                               storage_id=self.id)
        self.deleted = True
        return super().save(commit)

    def update(self, commit=True, **kwargs):
        GarbageStorages.create(path=self.path,
                               storetype=self.storetype,
                               storage_id=self.id)
        self.save_store()
        return super().update(commit=commit, **kwargs)

class Storages(StoragesCRUDMixin, Model, SurrogatePK):
    '''
    文件管理表

    :param          name: str(256)                  文件名
    :param          filetype: str(256)              文件类型
    :param          storetype: str(256)             存储类型
    :param          date: Date                      文件创建日期
    :param          saved: bool                     是否保存
    :param          path: str(2000)                 保存路径
    :param          uid: int                        用户ID
    :param          _store: FileStorage             文件
    '''

    name = db.Column(db.String(256), nullable=True, doc='文件名')
    filetype = db.Column(db.String(256), nullable=True, doc='文件类型')
    storetype = db.Column(db.String(256), nullable=True, doc='存储类型')
    date = db.Column(db.Date, nullable=True, doc='文件日期', default=local.date)
    saved = db.Column(db.Boolean, nullable=True, default=False, doc='是否保存')
    path = db.Column(db.String(2000), nullable=True, doc='文件路径')
    uid = db.Column(db.Integer, doc='用户ID')

    _store = None

    def __init__(self, **kwargs):
        self.store = kwargs.pop('store', None)
        db.Model.__init__(self, **kwargs)

    def _get_store(self):
        '''
        根据文件路径获取文件
        '''
        content_type = (
            mimetypes.guess_type(self.name)[0] or "application/octet-stream"
        )
        file = open(self.store_path.joinpath(self.path), 'rb')
        return FileStorage(file, self.name, 'file', content_type)

    @property
    def store(self):
        if self._store is None and self.saved:
            self._store = self._get_store()
        return self._store

    @store.setter
    def store(self, val):
        self._store = val

    @property
    def store_path(self):
        '''
        保存路径
        '''
        return Path(current_app.instance_path).parent\
            .joinpath('uploads',
                      self.storetype)

    def save_store(self):
        '''
        存储文件

        每一次存储文件都会生成一个新的地址
        '''
        self.saved = True if self.path is not None else False
        if self.storetype is None:
            raise ValueError("文件类型不能为空")
        if self.date is None:
            self.date = local.localdate().date()

        date_dir = Path(str(self.date.year),
                        str(self.date.month),
                        str(self.date.day))

        dirname = self.store_path.joinpath(date_dir)
        if not dirname.exists():
            dirname.mkdir(parents=True)
        secure_name = uuid4().hex

        savepath = str(dirname.joinpath(secure_name))
        if self.store is not None:
            self.store.save(savepath)
            self.filetype = self.store.content_type
            self.path = str(date_dir.joinpath(secure_name))
            self.saved = True

class GarbageStorages(SurrogatePK, Model):
    """
    回收站

    :param          path: str(2000)                 文件路径
    :param          storetype: str(256)             存储类型
    :param          storage_id: int                 存储ID
    :param          storage: Storages               关联Storages项
    """
    __tablename__ = "garbage_storages"

    path = db.Column(db.String(2000), nullable=True, doc='文件路径')
    storetype = db.Column(db.String(256), nullable=True, doc='存储类型')
    storage_id = db.Column(db.Integer, doc='文件ID')
    storage = db.relationship("Storages",
                              primaryjoin="GarbageStorages.storage_id == Storages.id",
                              foreign_keys=storage_id)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def hard_delete(self, commit=True):
        '''
        永久删除
        '''
        white_lst = ['default/AdminAvator.jpg', 'default/DefaultAvator.jpg']
        if self.filepath.exists() and self.path not in white_lst:
            logger.warning(f"deleted file: {self.filepath}")
            os.remove(self.filepath)
        if self.storage.deleted is True:
            self.storage.hard_delete()
        super().hard_delete()

    @property
    def filepath(self):
        return self.store_path.joinpath(self.path)

    @property
    def store_path(self):
        return Path(current_app.instance_path).parent\
            .joinpath('uploads',
                      self.storetype)
