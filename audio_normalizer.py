"""
简化版音量归一化 - 不依赖 pydub
使用基于文件大小的简单估算方法
"""
import os
import json


class SimpleAudioNormalizer:
    """
    简化版音频归一化处理器
    不需要 pydub，使用简单的文件大小估算
    """

    def __init__(self):
        self.cache_file = "audio_volume_cache_simple.json"
        self.volume_cache = self.load_cache()

        # 预设的常见音量调整值（基于经验）
        self.format_adjustments = {
            '.mp3': 1.0,   # MP3 通常音量正常
            '.wav': 0.8,   # WAV 通常音量较大
            '.flac': 0.9,  # FLAC 音量适中
            '.m4a': 1.1,   # M4A 通常音量较小
            '.ogg': 1.0,   # OGG 音量正常
            '.wma': 0.95,  # WMA 略大
        }

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
        """
        简单分析音频文件的音量
        基于文件大小和格式进行估算
        """
        # 检查缓存
        file_key = f"{file_path}_{os.path.getmtime(file_path)}"
        if file_key in self.volume_cache:
            return self.volume_cache[file_key]

        try:
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1].lower()

            # 基础调整值（基于格式）
            base_adjustment = self.format_adjustments.get(ext, 1.0)

            # 获取文件大小（MB）
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # 基于文件大小的微调
            # 假设：较大的文件可能比特率更高，音质更好，可能需要略微降低音量
            if file_size_mb > 10:
                size_adjustment = 0.95
            elif file_size_mb > 5:
                size_adjustment = 0.98
            else:
                size_adjustment = 1.0

            # 综合调整
            final_adjustment = base_adjustment * size_adjustment

            # 缓存结果
            self.volume_cache[file_key] = final_adjustment
            self.save_cache()

            print(f"📊 {os.path.basename(file_path)}: 调整倍数 {final_adjustment:.2f}")

            return final_adjustment

        except Exception as e:
            print(f"⚠️ 分析音量失败 {os.path.basename(file_path)}: {e}")
            return 1.0

    def get_volume_multiplier(self, file_path):
        """
        获取音量调整倍数（用于 QMediaPlayer）

        返回值: 0.5 - 1.5 的倍数
        """
        multiplier = self.analyze_volume(file_path)

        # 限制在合理范围内
        multiplier = max(0.5, min(1.5, multiplier))

        return multiplier

    def batch_analyze(self, file_paths, progress_callback=None):
        """
        批量分析音频文件

        Args:
            file_paths: 文件路径列表
            progress_callback: 进度回调函数 (current, total)
        """
        total = len(file_paths)

        for i, file_path in enumerate(file_paths, 1):
            if os.path.exists(file_path):
                self.analyze_volume(file_path)

                if progress_callback:
                    progress_callback(i, total)

        print(f"✅ 已分析 {total} 个音频文件的音量（简化模式）")

    def clear_cache(self):
        """清空音量缓存"""
        self.volume_cache.clear()
        self.save_cache()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("🗑️ 音量缓存已清空")


# 全局音量归一化器实例（简化版）
simple_normalizer = SimpleAudioNormalizer()


# ============ 兼容性包装器 ============
# 提供与原版 audio_normalizer 相同的接口

HAS_PYDUB = False  # 标记为简化版

class AudioNormalizer:
    """兼容性包装器，使用简化版归一化"""

    def __init__(self):
        self.normalizer = simple_normalizer
        self.cache_file = self.normalizer.cache_file
        self.volume_cache = self.normalizer.volume_cache

    def load_cache(self):
        return self.normalizer.load_cache()

    def save_cache(self):
        return self.normalizer.save_cache()

    def analyze_volume(self, file_path):
        return self.normalizer.analyze_volume(file_path)

    def get_volume_multiplier(self, file_path):
        return self.normalizer.get_volume_multiplier(file_path)

    def batch_analyze(self, file_paths, progress_callback=None):
        return self.normalizer.batch_analyze(file_paths, progress_callback)

    def clear_cache(self):
        return self.normalizer.clear_cache()


audio_normalizer = AudioNormalizer()

print("ℹ️ 使用简化版音量归一化（不依赖 pydub）")
print("💡 建议：安装 pydub 和 ffmpeg 以获得更精确的音量分析")