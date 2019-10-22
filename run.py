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
运行服务器
"""

from eventlet import monkey_patch
import sys

monkey_patch()


def main():
    """
    主函数
    """
    import argparse

    parser = argparse.ArgumentParser(description='运行Web服务器主程序脚本')
    parser.add_argument('-b', '--host', type=str, action='store', default='0.0.0.0',
                        help='设置服务器默认IP(默认：0.0.0.0)')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='开启DEBUG模式 (默认: 关闭')
    parser.add_argument('-r', '--use-reloader', action='store_true', default=False,
                        help='开启重加载模式 (默认: 关闭)')
    parser.add_argument('-p', '--port', action='store',
                        type=int, default=8000,
                        help='设置Web服务器开放端口(默认: 8000)')
    args = parser.parse_args()

    from app.app import app
    from app.extensions import socketio

    socketio.run(app, host=args.host, debug=args.debug,
                 use_reloader=args.use_reloader, port=args.port)


if __name__ == '__main__':
    sys.exit(main())
