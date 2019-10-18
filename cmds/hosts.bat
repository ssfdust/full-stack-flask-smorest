@echo off
set hosts="c:\WINDOWS\system32\drivers\etc\hosts"
set ip="192.168.3.42"
echo %ip% www.myproject.com>%hosts%
