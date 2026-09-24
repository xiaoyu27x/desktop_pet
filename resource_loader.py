"""
资源加载器 - 运行时从加密包读取资源
用法：在项目里 import resource_loader，替换所有直接的文件路径读取

    from resource_loader import res

    # 读取图片（返回 bytes，传给 QPixmap.loadFromData）
    pixmap = QPixmap()
    pixmap.loadFromData(res.read("resources/pet.png"))

    # 直接返回 QPixmap
    pixmap = res.qpixmap("resources/pet.png")

    # 音效/音乐需要文件路径时，解密到临时文件
    sound_path = res.extract_temp("resources/alert.mp3")
    sound_path = res.extract_temp("resources/default_music/song.mp3")
"""
import os
import io
import json
import struct
import hashlib
import tempfile
import atexit
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ============================================================
# 必须和 pack_resources.py 里的 PASSPHRASE 一致
PASSPHRASE  = "deskpet-zeph-2024-secret"
PACK_FILE   = "resources.dat"
MAGIC       = b"DPAK"
# ============================================================

class ResourceLoader:
    def __init__(self):
        self._key      = hashlib.sha256(PASSPHRASE.encode("utf-8")).digest()
        self._aesgcm   = AESGCM(self._key)
        self._index    = None   # {name: {offset, size, nonce_hex}}
        self._data_start = 0    # 数据区在文件中的起始位置
        self._pack_path  = None
        self._temp_files = []   # 记录临时文件，退出时清理

        atexit.register(self._cleanup)
        self._load_index()

    def _load_index(self):
        """加载并解密索引"""
        path = Path(PACK_FILE)
        if not path.exists():
            print(f"⚠️ ResourceLoader: 找不到 {PACK_FILE}，将直接从文件系统读取资源")
            return

        with open(path, "rb") as f:
            magic = f.read(4)
            if magic != MAGIC:
                print(f"❌ ResourceLoader: {PACK_FILE} 格式不正确")
                return

            idx_len   = struct.unpack("<I", f.read(4))[0]
            idx_nonce = f.read(12)
            idx_enc   = f.read(idx_len)

            # 解密索引
            idx_json  = self._aesgcm.decrypt(idx_nonce, idx_enc, None)
            entries   = json.loads(idx_json.decode("utf-8"))

            self._index = {e["name"]: e for e in entries}
            self._data_start = f.tell()   # 当前位置就是数据区起始
            self._pack_path  = str(path)

        print(f"✅ ResourceLoader: 已加载资源包，共 {len(self._index)} 个文件")

    def available(self) -> bool:
        """是否有可用的资源包"""
        return self._index is not None

    def read(self, name: str) -> bytes:
        """
        读取资源为 bytes。
        name 示例: "resources/pet.png" 或 "resources/icons/tray.ico"
        """
        # 统一用正斜杠
        name = name.replace("\\", "/")

        # 有资源包则从包里读
        if self._index is not None:
            if name in self._index:
                return self._read_from_pack(name)
            else:
                print(f"⚠️ ResourceLoader: 包内找不到 {name}，尝试文件系统")

        # 回退到文件系统（开发时方便）
        if os.path.exists(name):
            with open(name, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"资源不存在: {name}")

    def _read_from_pack(self, name: str) -> bytes:
        entry   = self._index[name]
        nonce   = bytes.fromhex(entry["nonce_hex"])
        size    = entry["size"]
        offset  = entry["offset"]

        with open(self._pack_path, "rb") as f:
            f.seek(self._data_start + offset)
            enc = f.read(size)

        return self._aesgcm.decrypt(nonce, enc, None)

    def extract_temp(self, name: str, suffix: str = None) -> str:
        """
        解密并写入临时文件，返回临时文件路径。
        适合需要文件路径的场景（如 playsound）。
        """
        name = name.replace("\\", "/")

        if suffix is None:
            suffix = Path(name).suffix

        data = self.read(name)
        tmp  = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix,
            prefix="deskpet_res_"
        )
        tmp.write(data)
        tmp.close()

        self._temp_files.append(tmp.name)
        return tmp.name

    def qpixmap(self, name: str):
        """直接返回 QPixmap（需要 PyQt5 环境）"""
        from PyQt5.QtGui import QPixmap
        data  = self.read(name)
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        return pixmap

    def _cleanup(self):
        """程序退出时清理临时文件"""
        for path in self._temp_files:
            try:
                os.remove(path)
            except Exception:
                pass

# 全局单例
res = ResourceLoader()