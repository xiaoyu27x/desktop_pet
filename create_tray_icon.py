"""
将宠物图片转换为托盘图标（优化版 - 裁剪中心区域）
运行方法: python create_tray_icon.py
也可以在程序启动时被 mainpet.py 自动调用
"""

from PIL import Image
import os


def create_tray_icon():
    """创建托盘图标 - 裁剪中心区域放大"""

    # 搜索顺序：resources/ 优先，pet2 优先
    source_candidates = [
        "resources/pet2.png",
        "resources/pet.png",
        "resources/pet.jpg",
        "resources/pet.gif",
        "pet2.png",
        "pet.png",
        "pet.jpg",
        "pet.gif",
    ]

    # 如果已经有图标就跳过（避免每次启动都重新生成）
    if (os.path.exists("resources/icons/tray_icon.ico") and
            os.path.exists("resources/icons/tray_icon.png")):
        return True

    source = None
    for f in source_candidates:
        if os.path.exists(f):
            source = f
            break

    if not source:
        print("❌ 未找到宠物图片文件，无法生成托盘图标")
        return False

    print(f"📁 生成托盘图标，源文件: {source}")

    try:
        img = Image.open(source).convert("RGBA")
        width, height = img.size

        os.makedirs("resources/icons", exist_ok=True)

        # 裁剪中心 60% 区域
        crop_size = min(width, height) * 0.6
        left   = (width  - crop_size) / 2
        top    = (height - crop_size) / 2
        right  = left + crop_size
        bottom = top  + crop_size
        img_cropped = img.crop((left, top, right, bottom))

        # 32x32 PNG
        icon_32 = img_cropped.resize((32, 32), Image.Resampling.LANCZOS)
        icon_32.save("resources/icons/tray_icon.png")

        # ICO（含 16x16 和 32x32）
        icon_32.save(
            "resources/icons/tray_icon.ico",
            format='ICO',
            sizes=[(16, 16), (32, 32)]
        )

        print("✅ 托盘图标已生成: resources/icons/tray_icon.ico / .png")
        return True

    except Exception as e:
        print(f"❌ 生成托盘图标失败: {e}")
        return False


if __name__ == "__main__":
    # 强制重新生成
    for f in ["resources/icons/tray_icon.ico", "resources/icons/tray_icon.png"]:
        if os.path.exists(f):
            os.remove(f)
    create_tray_icon()