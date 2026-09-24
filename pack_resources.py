"""
资源加密打包工具 - 适配 DeskPet 项目结构
用法：python pack_resources.py
"""
import os
import json
import struct
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ============================================================
# 配置区
# ============================================================
OUTPUT_FILE = "resources.dat"
PASSPHRASE  = "deskpet-zeph-2024-secret"   # ⚠️ 改成你自己的，不要泄露

# 手动指定的单个文件（不需要，留空即可）
RESOURCE_FILES = []

# 自动扫描整个 resources/ 目录（含子目录 icons/ default_music/ 等）
SCAN_DIRS  = ["resources"]
SCAN_EXTS  = {".png", ".jpg", ".jpeg", ".ico", ".bmp", ".gif", ".webp",
              ".mp3", ".m4a", ".wav", ".ogg", ".flac"}
# ============================================================


def derive_key(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def collect_files():
    collected = {}
    for real_path, key_name in RESOURCE_FILES:
        if Path(real_path).exists():
            collected[key_name] = real_path
        else:
            print(f"  ⚠️ 跳过（不存在）: {real_path}")
    for scan_dir in SCAN_DIRS:
        p = Path(scan_dir)
        if not p.exists():
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix.lower() in SCAN_EXTS:
                key = f.as_posix()
                if key not in collected:
                    collected[key] = str(f)
    return list(collected.items())


def pack():
    key    = derive_key(PASSPHRASE)
    aesgcm = AESGCM(key)

    files = collect_files()
    if not files:
        print("❌ 没有找到任何资源文件，请检查配置")
        return

    print(f"📦 准备打包 {len(files)} 个文件...\n")

    index            = []
    encrypted_chunks = []
    offset           = 0

    for key_name, real_path in files:
        raw       = Path(real_path).read_bytes()
        nonce     = os.urandom(12)
        encrypted = aesgcm.encrypt(nonce, raw, None)
        index.append({"name": key_name, "offset": offset,
                       "size": len(encrypted), "nonce_hex": nonce.hex()})
        encrypted_chunks.append(encrypted)
        offset += len(encrypted)
        print(f"  ✅ {key_name:<30}  {len(raw):>8,} → {len(encrypted):>8,} bytes")

    idx_json      = json.dumps(index, ensure_ascii=False).encode("utf-8")
    idx_nonce     = os.urandom(12)
    idx_encrypted = aesgcm.encrypt(idx_nonce, idx_json, None)

    with open(OUTPUT_FILE, "wb") as out:
        out.write(b"DPAK")
        out.write(struct.pack("<I", len(idx_encrypted)))
        out.write(idx_nonce)
        out.write(idx_encrypted)
        for chunk in encrypted_chunks:
            out.write(chunk)

    total_in  = sum(Path(rp).stat().st_size for _, rp in files)
    total_out = Path(OUTPUT_FILE).stat().st_size
    print(f"\n{'─'*55}")
    print(f"🎉 打包完成！  →  {OUTPUT_FILE}  ({total_out/1024:.1f} KB)")
    print(f"   原始总大小: {total_in/1024:.1f} KB")
    print(f"\n💡 发布时只需带 {OUTPUT_FILE}，不需要带原始 .png/.mp3 文件")


if __name__ == "__main__":
    pack()