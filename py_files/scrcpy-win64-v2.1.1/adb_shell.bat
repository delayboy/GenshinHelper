@echo off
set NOW_BAT_DIR=""%~s0""
echo "/c %NOW_BAT_DIR% ::"
%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %NOW_BAT_DIR% ::","","runas",1)(window.close)&&exit
cd /d "%~dp0"
adb.exe devices
adb.exe -s QWBILZRGSW7XXCV4 forward tcp:80 tcp:9999
adb forward --list
pause