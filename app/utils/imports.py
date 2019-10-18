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

import pkgutil

def import_submodules(context: dict, root_module: str, path: str):
    """
    加载文件夹下的所有子模块
    https://github.com/getsentry/zeus/blob/97528038a0abfd6f0e300d8d3f276e1b0818c328/zeus/utils/imports.py#L23
    >>> import_submodules(locals(), __name__, __path__)
    """
    modules = {}
    for loader, module_name, is_pkg in pkgutil.walk_packages(path, root_module + "."):
        # this causes a Runtime error with model conflicts
        # module = loader.find_module(module_name).load_module(module_name)
        module = __import__(module_name, globals(), locals(), ["__name__"])
        keys = getattr(module, "__all__", None)
        if keys is None:
            keys = [k for k in vars(module).keys() if not k.startswith("_")]

        for k in keys:
            context[k] = getattr(module, k, None)
        modules[module_name] = module

    # maintain existing module namespace import with priority
    for k, v in modules.items():
        context[k] = v
