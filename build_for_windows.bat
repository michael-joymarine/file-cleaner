@echo off
chcp 65001 >nul
echo ================================================
echo   定时文件清理工具 - Windows 打包程序
echo   Joy Marine 专用版
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检查 Python 版本...
python --version

echo.
echo [2/4] 安装 PyInstaller...
pip install pyinstaller schedule --quiet
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)
echo [完成] PyInstaller 安装成功

echo.
echo [3/4] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 获取当前目录
set SCRIPT_DIR=%~dp0
set SOURCE_FILE=%SCRIPT_DIR%file_cleaner_windows.py
set OUTPUT_DIR=%SCRIPT_DIR%dist

REM 检查源码文件
if not exist "%SOURCE_FILE%" (
    echo [错误] 未找到 file_cleaner_windows.py
    echo 请确保此脚本与源码文件在同一目录
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM 执行打包
pyinstaller ^
    --name="定时文件清理工具" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="%USERPROFILE%\.workbuddy;." ^
    "%SOURCE_FILE%" ^
    --distpath="%OUTPUT_DIR%" ^
    --workpath="%SCRIPT_DIR%build" ^
    --specpath="%SCRIPT_DIR%"

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo [4/4] 清理临时文件...
rmdir /s /q "%SCRIPT_DIR%build" 2>nul
rmdir /s /q "%SCRIPT_DIR%__pycache__" 2>nul
del /f /q "%SCRIPT_DIR%*.spec" 2>nul

echo.
echo ================================================
echo   打包完成！
echo ================================================
echo.
echo exe 文件位置:
echo %OUTPUT_DIR%\定时文件清理工具.exe
echo.
echo 可以直接双击运行，无需安装 Python
echo.
pause
