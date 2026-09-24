"""
音量归一化工具 - 使用 pydub 实现音量均衡化
需要安装: pip install pydub
需要 ffmpeg 支持
"""
import os
import json
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.effects import normalize

    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("⚠️ 未安装 pydub，音量归一化功能不可用")
    print("安装方法: pip install pydub")
    print("还需要安装 ffmpeg: https://ffmpeg.org/download.html")


class AudioNormalizer:
    """音频归一化处理器"""

    def __init__(self):
        self.cache_file = "audio_volume_cache.json"
        self.volume_cache = self.load_cache()
        self.target_dBFS = -20.0  # 目标音量（分贝）

    def load_cache(self):
        """加载音量缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        """保存音量缓存"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.volume_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存音量缓存失败: {e}")

    def analyze_volume(self, file_path):
        """分析音频文件的音量"""
        if not HAS_PYDUB:
            return 0

        # 检查缓存
        file_key = f"{file_path}_{os.path.getmtime(file_path)}"
        if file_key in self.volume_cache:
            return self.volume_cache[file_key]

        try:
            # 加载音频
            audio = AudioSegment.from_file(file_path)

            # 获取音量（dBFS）
            current_dBFS = audio.dBFS

            # 计算需要调整的音量（百分比）
            # dBFS 是负数，越接近 0 越大声
            volume_adjustment = self.target_dBFS - current_dBFS

            # 缓存结果
            self.volume_cache[file_key] = volume_adjustment
            self.save_cache()

            print(f"📊 {os.path.basename(file_path)}: {current_dBFS:.1f} dBFS → 调整 {volume_adjustment:+.1f} dB")

            return volume_adjustment

        except Exception as e:
            print(f"⚠️ 分析音量失败 {os.path.basename(file_path)}: {e}")
            return 0

    def get_volume_multiplier(self, file_path):
        """
        获取音量调整倍数（用于 QMediaPlayer）

        返回值: 0.0 - 2.0 的倍数
        """
        if not HAS_PYDUB:
            return 1.0

        adjustment_dB = self.analyze_volume(file_path)

        # 将 dB 转换为倍数
        # dB = 20 * log10(multiplier)
        # multiplier = 10^(dB/20)
        import math
        multiplier = math.pow(10, adjustment_dB / 20.0)

        # 限制在合理范围内
        multiplier = max(0.1, min(2.0, multiplier))

        return multiplier

    def batch_analyze(self, file_paths, progress_callback=None):
        """
        批量分析音频文件

        Args:
            file_paths: 文件路径列表
            progress_callback: 进度回调函数 (current, total)
        """
        if not HAS_PYDUB:
            print("⚠️ 需要安装 pydub 才能使用音量归一化功能")
            return

        total = len(file_paths)

        for i, file_path in enumerate(file_paths, 1):
            if os.path.exists(file_path):
                self.analyze_volume(file_path)

                if progress_callback:
                    progress_callback(i, total)

        print(f"✅ 已分析 {total} 个音频文件的音量")

    def clear_cache(self):
        """清空音量缓存"""
        self.volume_cache.clear()
        self.save_cache()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("🗑️ 音量缓存已清空")


# 全局音量归一化器实例
audio_normalizer = AudioNormalizer()