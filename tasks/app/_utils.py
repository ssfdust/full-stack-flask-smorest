# encoding: utf-8
"""
Invoke中App相关工具
"""
import functools
import platform

try:
    import readline
except ImportError:
    pass

from invoke import Task as BaseTask


class Task(BaseTask):
    """
    封装Task以便于支持装饰器
    """

    def argspec(self, body):
        """
        详情： https://github.com/pyinvoke/invoke/pull/399.
        """
        if hasattr(body, "__wrapped__"):
            return self.argspec(body.__wrapped__)
        return super(Task, self).argspec(body)


def app_context_task(*args, **kwargs):
    """
    Invoke中应用的app_context

    示例:

    >>> @app_context_task
    ... def my_task(context, some_arg, some_option='default'):
    ...     print("Done")

    >>> @app_context_task(
    ...     help={'some_arg': "This is something useful"}
    ... )
    ... def my_task(context, some_arg, some_option='default'):
    ...     print("Done")
    """
    if len(args) == 1:
        func = args[0]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            A wrapped which tries to get ``app`` from ``kwargs`` or creates a
            new ``app`` otherwise, and actives the application context, so the
            decorated function is run inside the application context.
            """
            app = kwargs.pop("app", None)
            if app is None:
                from app.app import app

            with app.app_context():
                return func(*args, **kwargs)

        # This is the default in Python 3, so we just make it backwards
        # compatible with Python 2
        if not hasattr(wrapper, "__wrapped__"):
            wrapper.__wrapped__ = func
        return Task(wrapper, **kwargs)

    return lambda func: app_context_task(func, **kwargs)


def rlinput(prompt, prefill=""):
    if platform.system() == "Windows":
        from .winpress import sendkeys

        sendkeys(prefill)
        return input(prompt)
    else:
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
        try:
            return input(prompt)  # or raw_input in Python 2
        finally:
            readline.set_startup_hook()
