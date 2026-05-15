#!/bin/bash
# 定时文件清理工具启动脚本 - Joy Marine

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="/Users/michael/.workbuddy/binaries/python/versions/3.13.12/bin/python3"

exec "$PYTHON" "$SCRIPT_DIR/file_cleaner.py"
