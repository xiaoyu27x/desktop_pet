"""
优化版动画模块 - 弹跳效果（修复形变与去重版）
"""
from PyQt5.QtCore import QTimer, Qt
import math

class AnimationManager:
    def __init__(self, pet):
        self.pet = pet
        self.original_pixmap = None  # 保存原始图片
        self.is_playing = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)

    def save_original_pixmap(self):
        """保存原始高质量图片，用于后续平滑缩放"""
        if hasattr(self.pet, 'pet_label') and self.pet.pet_label.pixmap():
            self.original_pixmap = self.pet.pet_label.pixmap().copy()
            # 确保标签居中对齐
            self.pet.pet_label.setAlignment(Qt.AlignCenter)

    def stretch_on_click(self):
        """点击动画：物理感挤压拉伸效果"""
        if self.is_playing:
            return

        self.is_playing = True

        # 保存开始动画前的原始状态
        self.original_width = self.pet.width()
        self.original_height = self.pet.height()
        self.original_x = self.pet.x
        self.original_y = self.pet.y

        # 计算并保存固定的中心点，确保缩放时宠物不会“位移”
        self.fixed_center_x = self.original_x + self.original_width / 2
        self.fixed_center_y = self.original_y + self.original_height / 2

        if self.original_pixmap is None:
            self.save_original_pixmap()

        # 动画参数
        self.animation_frame = 0
        self.total_frames = 20  # 缩短帧数让弹跳更脆
        self.bounce_amplitude = 0.25  # 增加振幅，效果更明显

        # 开始动画前停止移动
        if hasattr(self.pet, 'movement'):
            self.pet.movement.stop_moving()

        self.animation_timer.start(25)  # 25ms一帧

    def _update_animation(self):
        """更新动画帧 - 实现横纵交替缩放"""
        if not self.is_playing:
            return

        self.animation_frame += 1

        if self.animation_frame <= self.total_frames:
            # 计算进度 (0.0 到 1.0)
            progress = self.animation_frame / self.total_frames

            # 使用带衰减的正弦波：弹两下
            # bounce 的值在 -1 到 1 之间波动，随时间减弱
            decay = math.exp(-progress * 3)  # 指数衰减
            bounce = math.sin(progress * math.pi * 3) * decay

            # 挤压拉伸逻辑：横向放大时纵向缩小，反之亦然
            width_scale = 1 + bounce * self.bounce_amplitude
            height_scale = 1 - bounce * self.bounce_amplitude

            current_width = max(20, int(self.original_width * width_scale))
            current_height = max(20, int(self.original_height * height_scale))

            self._apply_transform(current_width, current_height)
        else:
            self._end_animation()

    def _apply_transform(self, width, height):
        """执行窗口和图片的变换"""
        # 1. 保持中心点不变计算新坐标
        new_x = int(self.fixed_center_x - width / 2)
        new_y = int(self.fixed_center_y - height / 2)

        # 2. 调整窗口位置和尺寸
        self.pet.move(new_x, new_y)
        self.pet.resize(width, height)

        # 3. 缩放图片
        if self.original_pixmap and hasattr(self.pet, 'pet_label'):
            self.pet.pet_label.resize(width, height)

            # 关键：这里必须用 IgnoreAspectRatio 才能看到挤压变形效果
            scaled_pixmap = self.original_pixmap.scaled(
                width, height,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            self.pet.pet_label.setPixmap(scaled_pixmap)

    def stop_animation(self):
        """强制停止动画并恢复"""
        if self.is_playing:
            self._end_animation()

    def _end_animation(self):
        """动画结束：重置所有状态"""
        self.animation_timer.stop()

        # 恢复图片到原始比例
        if self.original_pixmap and hasattr(self.pet, 'pet_label'):
            self.pet.pet_label.setAlignment(Qt.AlignCenter)
            self.pet.pet_label.setPixmap(
                self.original_pixmap.scaled(
                    self.original_width, self.original_height,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

        # 恢复窗口到原始位置和大小
        self.pet.resize(self.original_width, self.original_height)
        self.pet.move(self.original_x, self.original_y)

        # 同步更新主窗口内部坐标变量
        self.pet.x = self.original_x
        self.pet.y = self.original_y

        self.is_playing = False

        # 通知交互模块
        if hasattr(self.pet, 'interaction'):
            self.interaction = self.pet.interaction
            self.interaction.is_animating = False

        # 恢复自动移动
        if hasattr(self.pet, 'movement'):
            self.pet.movement.start_moving()