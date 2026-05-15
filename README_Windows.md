# 定时文件清理工具 - Windows 版本

Joy Marine 专用版

## 📦 打包方式

### 方式一：Windows 本地打包（推荐）

1. 把整个文件夹复制到 Windows 10/11 电脑
2. 双击运行 `build_for_windows.bat`
3. 等待 2-5 分钟
4. 在 `dist` 文件夹找到生成的 exe

### 方式二：GitHub Actions 云端打包（无需 Windows）

1. 在 GitHub 创建新仓库
2. 上传所有文件
3. 进入 Actions 页面，会自动触发构建
4. 下载生成的 exe 文件

详细步骤：

```
1. 登录 GitHub → Create new repository
2. Repository name: file-cleaner
3. Private → Create repository
4. 上传以下文件：
   - file_cleaner_windows.py
   - build_for_windows.bat
   - .github/workflows/build.yml
5. 进入 Actions 标签页
6. 点击 "Build Windows EXE" workflow
7. 点击 Run workflow
8. 等待完成后下载 artifact
```

## 🛠 功能

- ✅ 添加/移除监控文件夹
- ✅ 删除 N 天前的文件（可设置 1-365 天）
- ✅ 每天定时自动清理
- ✅ 实时日志显示
- ✅ 配置自动保存

## 📝 系统要求

- Windows 10/11 (64位)
- 无需安装 Python（exe 为绿色版）
