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

REM Bring the environment in line with uv.lock (creates it on first run,
REM fast once it matches; uv also fetches the pinned Python if missing)
uv sync --quiet

REM Start Streamlit detached + quiet (so this .bat can finish)
start "" /b cmd /c uv run streamlit run app.py --server.port %PORT% --server.headless true --browser.gatherUsageStats false ^>nul 2^>nul

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
