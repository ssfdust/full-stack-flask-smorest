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

import sys


def run_as_socketio(app, args):
    """在socketio中运行"""
    from app.extensions import socketio

    socketio.init_app(app)

    socketio.run(
        app,
        host=args.bind,
        debug=args.debug,
        use_reloader=args.use_reloader,
        port=args.port)


def run_as_gunicorn(app, args):
    """在gunicorn中运行"""
    from gunicorn.app.wsgiapp import WSGIApplication

    args = vars(args)
    args['worker_class'] = 'eventlet'
    args['workers'] = 1
    if args['debug']:
        args['loglevel'] = 'debug'

    class StandaloneApplication(WSGIApplication):

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    StandaloneApplication(app, args).run()


def main():
    """
    主函数
    """
    import argparse

    parser = argparse.ArgumentParser(description='运行Web服务器主程序脚本')
    parser.add_argument(
        '-a',
        '--admin',
        action='store_true',
        default=False,
        help='从admin启动(默认：否)')
    parser.add_argument(
        '-b',
        '--bind',
        type=str,
        action='store',
        default='127.0.0.1',
        help='设置服务器默认IP(默认：127.0.0.1)')
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        default=False,
        help='开启DEBUG模式 (默认: 关闭')
    parser.add_argument(
        '-r',
        '--use-reloader',
        action='store_true',
        default=False,
        help='开启重加载模式 (默认: 关闭)')
    parser.add_argument(
        '-g',
        '--gunicorn',
        action='store_true',
        default=False,
        help='开启重加载模式 (默认: 关闭)')
    parser.add_argument(
        '-p',
        '--port',
        action='store',
        type=int,
        default=8000,
        help='设置Web服务器开放端口(默认: 8000)')
    args = parser.parse_args()
    if not args.gunicorn:
        from eventlet import monkey_patch
        monkey_patch()

        func = run_as_socketio
    else:
        func = run_as_gunicorn

    if not args.admin:
        from app.app import app
    else:
        from admin.app import app

    func(app, args)


if __name__ == '__main__':
    sys.exit(main())
