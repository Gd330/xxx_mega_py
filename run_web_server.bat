@echo off
echo 正在清理系统临时文件和缓存...

:: 清理当前用户的临时文件夹（%TEMP%）
echo 正在清空 "%TEMP%" 文件夹...
del /q /f "%TEMP%\*.*" >nul 2>&1
for /d %%i in ("%TEMP%\*") do rd /s /q "%%i" >nul 2>&1

:: 清理 Windows 系统临时文件夹（需要管理员权限）
echo 正在清空 "C:\Windows\Temp" 文件夹...
del /q /f "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo 缓存清理完毕。
echo Starting the web service...
python app.py
pause
