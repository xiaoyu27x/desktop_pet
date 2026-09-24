"""
交互模块 - 旧版丝滑拖动 + 投掷速度 + 快捷键暂停
"""
from PyQt5.QtCore import Qt, QPoint, QTime
import random


class InteractionHandler:
    def __init__(self, pet):
        self.pet = pet
        self.dragging = False
        self.offset = QPoint()
        self.press_pos = QPoint()

        # 投掷速度追踪
        self.drag_positions = []
        self.drag_times = []
        self.max_history = 5

        # 暂停状态
        self.is_paused = False

    def handle_mouse_press(self, event, pet_instance):
        """按下：开始拖拽准备"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = event.pos()
            self.press_pos = event.globalPos()

            # 清空速度记录
            self.drag_positions.clear()
            self.drag_times.clear()

            # 停止自动移动
            if hasattr(pet_instance, 'movement'):
                pet_instance.movement.stop_moving()

    def handle_mouse_move(self, event, pet_instance):
        """移动：直接跟手，同时记录轨迹"""
        if not self.dragging:
            # 移动超过5像素才判定为拖拽
            if (event.globalPos() - self.press_pos).manhattanLength() > 5:
                self.dragging = True

        if self.dragging:
            new_pos = event.globalPos() - self.offset
            pet_instance.move(new_pos)
            pet_instance.x = new_pos.x()
            pet_instance.y = new_pos.y()

            # 记录轨迹用于计算投掷速度
            self.drag_positions.append(QPoint(new_pos.x(), new_pos.y()))
            self.drag_times.append(QTime.currentTime())

            if len(self.drag_positions) > self.max_history:
                self.drag_positions.pop(0)
                self.drag_times.pop(0)

    def handle_mouse_release(self, event, pet_instance):
        """松手：点击触发动画，拖拽应用投掷速度"""
        if event.button() == Qt.LeftButton:
            if not self.dragging:
                # 判定为点击：触发动画
                if hasattr(pet_instance, 'animation'):
                    pet_instance.animation.stretch_on_click()

            if hasattr(pet_instance, 'movement'):
                self._apply_drag_velocity()
                pet_instance.movement.start_moving()

            self.dragging = False

    def toggle_pause(self, pet_instance=None):
        """切换暂停状态（由快捷键调用）"""
        if pet_instance is None:
            pet_instance = self.pet
        self.is_paused = not self.is_paused

        if self.is_paused:
            if hasattr(pet_instance, 'movement'):
                pet_instance.movement.stop_moving()
            print("⏸️  宠物已暂停（再次按快捷键恢复）")
        else:
            if hasattr(pet_instance, 'movement'):
                pet_instance.movement.start_moving()
            print("▶️  宠物已恢复移动")

    def _apply_drag_velocity(self):
        """根据拖拽最后几帧计算投掷速度"""
        if len(self.drag_positions) < 2 or not hasattr(self.pet, 'movement'):
            self._randomize_direction()
            return

        idx = -3 if len(self.drag_positions) >= 3 else -2
        start_pos = self.drag_positions[idx]
        end_pos = self.drag_positions[-1]
        start_time = self.drag_times[idx]
        end_time = self.drag_times[-1]

        time_diff = start_time.msecsTo(end_time)

        if time_diff <= 0:
            self._randomize_direction()
            return

        vx = (end_pos.x() - start_pos.x()) / time_diff
        vy = (end_pos.y() - start_pos.y()) / time_diff

        speed_factor = 400
        max_speed = 12

        new_speed_x = max(-max_speed, min(max_speed, vx * speed_factor))
        new_speed_y = max(-max_speed, min(max_speed, vy * speed_factor))

        if abs(new_speed_x) < 0.5 and abs(new_speed_y) < 0.5:
            self._randomize_direction()
        else:
            self.pet.movement.set_speed(new_speed_x, new_speed_y)
            self.pet.movement.was_thrown = True

    def _randomize_direction(self):
        """给一个随机游走速度"""
        if hasattr(self.pet, 'movement'):
            s = self.pet.movement.default_speed_x
            self.pet.movement.set_speed(
                random.choice([-s, s]),
                random.choice([-s, s])
            )