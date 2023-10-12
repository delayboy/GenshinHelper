@echo off
@title 自制启动器 by Benson
set NOW_BAT_DIR=""%~s0""
echo "/c %NOW_BAT_DIR% ::"
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %NOW_BAT_DIR% ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"

pyi-makespec pyd_main.py
pause
pyinstaller -option pyd_main.spec