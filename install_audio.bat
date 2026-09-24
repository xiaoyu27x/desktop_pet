@echo off
echo 正在安装音频处理依赖...
python -m pip install --upgrade pip
python -m pip install pydub
echo.
echo 安装完成！
echo.
echo 请手动安装 ffmpeg:
echo 1. 访问 https://ffmpeg.org/download.html
echo 2. 下载 Windows 版本
echo 3. 解压并添加到系统 PATH
pause