#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python/13615802#13615802
"""

try:
    import win32console
except ImportError:
    print("请通过`pip install pywin32`安装win32支持")
    import sys

    sys.exit(2)

_stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)


def sendkeys(string=""):
    keys = []
    for c in str(string):
        evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
        evt.Char = c
        evt.RepeatCount = 1
        evt.KeyDown = True
        keys.append(evt)

    _stdin.WriteConsoleInput(keys)
