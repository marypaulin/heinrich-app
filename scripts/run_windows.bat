@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Jump to project root (parent of this scripts/ folder)
cd /d "%~dp0\.."

set PORT=8502
set URL=http://localhost:%PORT%

REM If app already running, just open browser
powershell -NoProfile -Command ^
  "$p=%PORT%; if ((Test-NetConnection -ComputerName '127.0.0.1' -Port $p).TcpTestSucceeded) { exit 0 } else { exit 1 }"
if %errorlevel%==0 (
  start "" "%URL%"
  exit /b 0
)

REM Ensure venv exists
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment (.venv)...
  REM Prefer the Windows Python launcher if available
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
)

REM Activate venv
call ".venv\Scripts\activate.bat"

REM Install dependencies once (fast on later runs)
if not exist ".venv\.deps_installed" (
  echo Installing dependencies...
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  type nul > ".venv\.deps_installed"
)

REM Start Streamlit detached + quiet (so this .bat can finish)
start "" /b cmd /c python -m streamlit run app.py --server.port %PORT% --server.headless true --browser.gatherUsageStats false ^>nul 2^>nul

REM Wait until the port is listening (max ~15 seconds)
for /l %%i in (1,1,15) do (
  powershell -NoProfile -Command ^
    "$p=%PORT%; if ((Test-NetConnection -ComputerName '127.0.0.1' -Port $p).TcpTestSucceeded) { exit 0 } else { exit 1 }"
  if !errorlevel!==0 (
    timeout /t 1 /nobreak >nul
  ) else (
    goto :open
  )
)

:open
start "" "%URL%"

endlocal
