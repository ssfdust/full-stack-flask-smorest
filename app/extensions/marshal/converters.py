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
    app.extensions.marshal.converters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    类型转化模块

    此模块用以转换sqlalchemy中的自定义类型，以及
    marshmallow中不支持的类型。
    在marshmallow-sqlalchemy#75解决前都需要此方法
    issue地址：
    github.com/marshmallow-code/marshmallow-sqlalchemy/issues/75
"""

from marshmallow_sqlalchemy import ModelConverter as BaseModelConverter
from .fields import ArrowField


class ModelConverter(BaseModelConverter):
    """
    更新SQLA_TYPE_MAPPING， 为ModelConverter添加新的类型转换：

    ArrowType -> ArrowField
    """
    try:
        from app.extensions.sqla.types import ArrowType

        SQLA_TYPE_MAPPING = BaseModelConverter.SQLA_TYPE_MAPPING
        SQLA_TYPE_MAPPING[ArrowType] = ArrowField
    except ImportError:
        pass
