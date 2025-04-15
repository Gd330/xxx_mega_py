@echo off
echo Cleaning up system temporary files and caches...

:: Clear current user's temporary folder (%TEMP%)
echo Clearing the "%TEMP%" folder...
del /q /f "%TEMP%\*.*" >nul 2>&1
for /d %%i in ("%TEMP%\*") do rd /s /q "%%i" >nul 2>&1

:: Clear the Windows system temporary folder (requires administrator privileges)
echo Clearing the "C:\Windows\Temp" folder...
del /q /f "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo Cache cleanup completed.
echo Starting the web service...
python run.py
pause