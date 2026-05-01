@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   新兴支柱产业追踪系统 - 启动中...
echo ============================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [1/2] 安装依赖...
pip install -r requirements.txt -q

echo [2/2] 启动服务器...
echo.
echo ============================================
echo   服务器已启动
echo   访问地址: http://localhost:8765
echo   按 Ctrl+C 停止服务器
echo ============================================
echo.

python server.py
pause
