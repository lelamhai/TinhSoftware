@echo off
echo ========================================================================
echo  Cài Visual C++ Redistributable 2015-2022
echo ========================================================================
echo.
echo Downloading...

powershell -Command "& {Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'}"

echo.
echo Downloaded: vc_redist.x64.exe
echo.
echo Starting installation...
echo.

start /wait vc_redist.x64.exe /install /passive /norestart

echo.
echo ========================================================================
echo  Cài đặt hoàn tất!
echo ========================================================================
echo.
echo Bước tiếp theo:
echo 1. Restart máy tính (khuyến nghị)
echo 2. Chạy: python run.py
echo.
pause
