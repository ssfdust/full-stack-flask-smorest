#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


"""
    app.extensions.config
    ~~~~~~~~~~~~~~~~~~~~~~~~

    config模块

    源自：Flask-Environment
    由于pytoml已经不再支持以及源码不长故在重新在本地实现

    使用：
    >>> from flask import Flask as BaseFlask
    >>> from app.config import Config
    >>> class Flask(BaseFlask):
            config_class = Config
    >>> app = Flask('test')
    >>> app.config.from_toml('/path/to/toml_file')
"""

import os
import toml

from flask._compat import iteritems
from flask.config import Config as FlaskConfig


class ConfigError(Exception):
    pass


class Config(FlaskConfig):

    def __init__(self, root_path=None, defaults=None, app=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.from_mapping(app.config)
        app.config = self
        return self

    def from_toml(self, filename, environment=None):
        """Updates the values in the config from a TOML file. This function
        behaves as if the TOML object was a dictionary and passed to the
        :meth:`from_mapping` function.
        :param filename: the filename of the JSON file.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        """

        # Prepeend the root path is we don't have an absolute path
        filename = (os.path.join(self.root_path, filename)
                    if filename.startswith(os.sep)
                    else filename)

        try:
            with open(filename) as toml_file:
                obj = toml.load(toml_file)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise

        return self.from_mapping(obj)

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        .. versionadded:: 1.0
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self[key] = value
        return True

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """根据字符串返回和前缀相符合的Flask选项。

        示例用法:
        >>> app.config['IMAGE_STORE_TYPE'] = 'fs'
        >>> app.config['IMAGE_STORE_PATH'] = '/var/app/images'
        >>> app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
        >>> image_store_config = app.config.get_namespace('IMAGE_STORE_')

        结果字典`image_store`看上去像这样:
            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }
        当需要根据配置的参数，渲染为作为函数或类的传入参数时，这个方法
        十分不错。

        :param namespace: 配置的namespace
        :param lowercase: 选项是否转为小写的
        :param trim_namespace: 是否去除选项中的空格
        """
        rv = {}
        for k, v in iteritems(self):
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv
