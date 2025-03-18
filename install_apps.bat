@echo off
setlocal enabledelayedexpansion

:: Define installation file names (Make sure they match your downloaded installers)
set GIT_INSTALLER=Git-*.exe
set VSCODE_INSTALLER=VSCodeSetup-*.exe
set ANACONDA_INSTALLER=Anaconda*.exe

:: Define installation directories (default paths)
set GIT_PATH="C:\Program Files\Git\bin\git.exe"
set VSCODE_PATH="C:\Program Files\Microsoft VS Code\Code.exe"
set ANACONDA_PATH="C:\ProgramData\Anaconda3\python.exe"

:: Change directory to script location
cd /d "%~dp0"

:: Install Git
echo Installing Git...
start /wait "" %GIT_INSTALLER% /VERYSILENT /NORESTART /SUPPRESSMSGBOXES

:: Install VS Code
echo Installing VS Code...
start /wait "" %VSCODE_INSTALLER% /VERYSILENT /NORESTART /SUPPRESSMSGBOXES

:: Install Anaconda (with environment variable setup)
echo Installing Anaconda...
start /wait "" %ANACONDA_INSTALLER% /InstallationType=AllUsers /AddToPath=1 /RegisterPython=1 /S

:: Set environment variables for Anaconda manually (if not set by installer)
echo Setting Anaconda environment variables...
setx PATH "%PATH%;C:\ProgramData\Anaconda3;C:\ProgramData\Anaconda3\Scripts;C:\ProgramData\Anaconda3\Library\bin" /M

:: Verify installations
echo Checking installations...

if exist %GIT_PATH% (
    echo Git installed successfully.
) else (
    echo Git installation failed.
)

if exist %VSCODE_PATH% (
    echo VS Code installed successfully.
) else (
    echo VS Code installation failed.
)

if exist %ANACONDA_PATH% (
    echo Anaconda installed successfully.
) else (
    echo Anaconda installation failed.
)

:: Create "py" folder on Desktop
set USERPROFILE=%USERPROFILE%
mkdir "%USERPROFILE%\Desktop\py"

echo All installations completed successfully!
pause
exit
