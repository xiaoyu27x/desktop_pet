"""
音量归一化环境诊断脚本
用于检测 pydub 安装问题
"""
import sys
import subprocess

print("=" * 60)
print("🔍 环境诊断开始")
print("=" * 60)

# 1. 检查 Python 版本和路径
print(f"\n1️⃣ Python 信息:")
print(f"   版本: {sys.version}")
print(f"   路径: {sys.executable}")

# 2. 检查 pip 版本
print(f"\n2️⃣ pip 信息:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                          capture_output=True, text=True)
    print(f"   {result.stdout.strip()}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 3. 尝试导入 pydub
print(f"\n3️⃣ pydub 检测:")
try:
    import pydub
    print(f"   ✅ pydub 已安装")
    print(f"   版本: {pydub.__version__ if hasattr(pydub, '__version__') else '未知'}")
    print(f"   路径: {pydub.__file__}")
except ImportError as e:
    print(f"   ❌ pydub 未安装或导入失败")
    print(f"   错误: {e}")

# 4. 检查 ffmpeg
print(f"\n4️⃣ ffmpeg 检测:")
try:
    result = subprocess.run(["ffmpeg", "-version"],
                          capture_output=True, text=True, timeout=3)
    if result.returncode == 0:
        first_line = result.stdout.split('\n')[0]
        print(f"   ✅ ffmpeg 已安装")
        print(f"   {first_line}")
    else:
        print(f"   ❌ ffmpeg 未正常工作")
except FileNotFoundError:
    print(f"   ❌ ffmpeg 未安装或不在 PATH 中")
except Exception as e:
    print(f"   ⚠️ 检测出错: {e}")

# 5. 列出已安装的包（部分）
print(f"\n5️⃣ 已安装的音频相关包:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"],
                          capture_output=True, text=True)
    lines = result.stdout.split('\n')
    audio_packages = [line for line in lines if any(keyword in line.lower()
                     for keyword in ['pydub', 'ffmpeg', 'audio', 'pyqt5'])]
    if audio_packages:
        for pkg in audio_packages:
            print(f"   {pkg}")
    else:
        print(f"   ⚠️ 未找到相关包")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 6. 提供安装建议
print("\n" + "=" * 60)
print("💡 安装建议:")
print("=" * 60)

print(f"\n如果 pydub 未安装，请使用以下命令（选择一个）:\n")
print(f"方法 1（推荐）:")
print(f"   {sys.executable} -m pip install pydub")

print(f"\n方法 2:")
print(f"   pip install pydub")

print(f"\n方法 3（使用国内镜像，更快）:")
print(f"   {sys.executable} -m pip install pydub -i https://pypi.tuna.tsinghua.edu.cn/simple")

print(f"\n如果 ffmpeg 未安装:")
print(f"   Windows: 下载 https://ffmpeg.org/download.html")
print(f"            解压后添加到系统环境变量 PATH")
print(f"   Mac:     brew install ffmpeg")
print(f"   Linux:   sudo apt-get install ffmpeg")

print("\n" + "=" * 60)
print("✅ 诊断完成")
print("=" * 60)

# 7. 尝试自动安装 pydub
print("\n❓ 是否尝试自动安装 pydub? (y/n): ", end='')
try:
    choice = input().strip().lower()
    if choice == 'y':
        print("\n🔧 正在安装 pydub...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pydub"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ pydub 安装成功！")
            print(result.stdout)
        else:
            print("❌ pydub 安装失败")
            print(result.stderr)
    else:
        print("⏭️  跳过自动安装")
except:
    print("\n⏭️  跳过自动安装")