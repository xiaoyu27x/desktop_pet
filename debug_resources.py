"""
快速诊断：检查 resources.dat 是否正确加载
把这个文件放到项目根目录，运行 python debug_resources.py
"""
import os

print(f"📂 当前工作目录: {os.getcwd()}")
print(f"📦 resources.dat 存在: {os.path.exists('resources.dat')}")
print()

try:
    from resource_loader import res
    print(f"✅ resource_loader 导入成功")
    print(f"✅ available: {res.available()}")
    print(f"📋 包内文件列表:")
    if res._index:
        for key in sorted(res._index.keys()):
            print(f"   {key}")
    else:
        print("   (空)")
except Exception as e:
    print(f"❌ resource_loader 导入失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试读取 pet2
try:
    data = res.read("resources/pet2.png")
    print(f"✅ 读取 resources/pet2.png 成功，大小: {len(data):,} bytes")
except Exception as e:
    print(f"❌ 读取 resources/pet2.png 失败: {e}")