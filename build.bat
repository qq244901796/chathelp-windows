@echo off
setlocal
cd /d "%~dp0"

REM One-click local build. ASCII only: Chinese Windows cmd is GBK.
REM Output: dist\chathelp-glm\chathelp-glm.exe

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtualenv .venv ...
    python -m venv .venv || goto :fail
)
call ".venv\Scripts\activate.bat" || goto :fail

echo Installing dependencies ...
python -m pip install -r requirements-lock.txt || goto :fail
python -m unittest discover -s tests -v || goto :fail

echo Building ...
pyinstaller --noconfirm --clean jev.spec || goto :fail

echo.
echo Build OK.
echo   %cd%\dist\chathelp-glm\chathelp-glm.exe
echo Ship the whole dist\chathelp-glm folder: the exe needs the files next to it.
pause
exit /b 0

:fail
echo.
echo Build FAILED. Scroll up for the error.
pause
exit /b 1
