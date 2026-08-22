@echo off
chcp 65001 >nul
title Agency Subagents - 繁體中文專家子代理管理器

echo ========================================================
echo   🎭 Agency Subagents - 繁體中文專家子代理管理器
echo ========================================================
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python，請確認已安裝 Python 3.10+ 並加入 PATH 環境變數。
    pause
    exit /b 1
)

REM 檢查虛擬環境是否存在
if not exist ".venv" (
    echo [資訊] 正在建立 Python 虛擬環境 (.venv)...
    python -m venv .venv
    echo [資訊] 正在安裝必要依賴模組...
    .venv\Scripts\pip.exe install -r requirements.txt
)

REM 自動開啟瀏覽器
echo [資訊] 正在啟動伺服器並開啟瀏覽器...
start "" "http://localhost:8000"

REM 啟動 FastAPI 服務
.venv\Scripts\python.exe app.py

pause
