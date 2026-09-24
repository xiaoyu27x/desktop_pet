"""
修复后的移动管理模块 - 添加速度衰减和窗口避让（优化平滑移出）
"""
import random
from PyQt5.QtCore import QTimer, QRect
from PyQt5.QtWidgets import QApplication

class MovementManager:
    def __init__(self, pet_instance):
        self.pet_instance = pet_instance
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_pet)

        # 初始速度
        self.speed_x = random.choice([-2, -1, 1, 2])
        self.speed_y = random.choice([-2, -1, 1, 2])

        # 保存默认速度（用于恢复）
        self.default_speed_x = self.speed_x
        self.default_speed_y = self.speed_y

        self.move_interval = 50
        self.is_moving = True

        # 速度衰减参数
        self.was_thrown = False  # 是否被投掷过
        self.decay_rate = 0.98  # 衰减率（越接近1衰减越慢）
        self.min_speed_threshold = 0.5  # 最小速度阈值

        # 窗口检测器引用（稍后设置）
        self.window_detector = None

        # 碰撞判定边距（像素）- 用于适应透明边框
        self.collision_margin = 20  # 默认向内收缩20像素

        # 初始化位置
        screen = QApplication.primaryScreen().geometry()

        if hasattr(self.pet_instance, 'pet_width'):
            pet_width = self.pet_instance.pet_width
            pet_height = self.pet_instance.pet_height
        else:
            pet_width = 140
            pet_height = 140

        max_x = max(1, screen.width() - pet_width)
        max_y = max(1, screen.height() - pet_height)

        self.pet_instance.x = random.randint(0, max_x)
        self.pet_instance.y = random.randint(0, max_y)

        if hasattr(self.pet_instance, 'update_position'):
            self.pet_instance.update_position(self.pet_instance.x, self.pet_instance.y)
        else:
            self.pet_instance.move(int(self.pet_instance.x), int(self.pet_instance.y))

    def start_moving(self):
        self.timer.start(self.move_interval)
        self.is_moving = True

    def stop_moving(self):
        self.timer.stop()
        self.is_moving = False

    def move_pet(self):
        if not self.is_moving:
            return

        # 如果被投掷过或处于逃逸状态（速度快），应用速度衰减
        # 这里增加了对默认速度倍率的检查
        if self.was_thrown or abs(self.speed_x) > abs(self.default_speed_x) * 1.1:
            self._apply_speed_decay()

        screen = QApplication.primaryScreen().geometry()
        boundary_buffer = 5

        if hasattr(self.pet_instance, 'pet_width'):
            pet_width = self.pet_instance.pet_width
            pet_height = self.pet_instance.pet_height
        else:
            pet_width = self.pet_instance.width()
            pet_height = self.pet_instance.height()

        # 计算新位置
        new_x = self.pet_instance.x + self.speed_x
        new_y = self.pet_instance.y + self.speed_y

        # 屏幕边界处理
        hit_boundary = False
        if new_x <= boundary_buffer:
            self.speed_x = abs(self.speed_x)
            new_x = boundary_buffer + 1
            hit_boundary = True
        elif new_x >= screen.width() - pet_width - boundary_buffer:
            self.speed_x = -abs(self.speed_x)
            new_x = screen.width() - pet_width - boundary_buffer - 1
            hit_boundary = True

        if new_y <= boundary_buffer:
            self.speed_y = abs(self.speed_y)
            new_y = boundary_buffer + 1
            hit_boundary = True
        elif new_y >= screen.height() - pet_height - boundary_buffer:
            self.speed_y = -abs(self.speed_y)
            new_y = screen.height() - pet_height - boundary_buffer - 1
            hit_boundary = True

        # 窗口碰撞检测
        if self.window_detector is not None:
            window_rect = self.window_detector.active_window_rect
            if window_rect is not None:
                # 计算收缩后的判定区域
                collision_left = new_x + self.collision_margin
                collision_right = new_x + pet_width - self.collision_margin
                collision_top = new_y + self.collision_margin
                collision_bottom = new_y + pet_height - self.collision_margin

                collision_rect = QRect(
                    int(collision_left),
                    int(collision_top),
                    int(collision_right - collision_left),
                    int(collision_bottom - collision_top)
                )

                # 检查是否发生碰撞或重叠
                if window_rect.intersects(collision_rect):
                    # 修改：调用优化后的碰撞处理逻辑
                    collision_handled_pos = self._handle_window_collision(
                        window_rect, new_x, new_y, pet_width, pet_height
                    )

                    if collision_handled_pos:
                        # 如果是边缘反弹，使用返回的修正位置
                        new_x, new_y = collision_handled_pos
                        hit_boundary = True
                    else:
                        # 如果是逃离模式（无坐标修正），重新计算当前帧位置
                        new_x = self.pet_instance.x + self.speed_x
                        new_y = self.pet_instance.y + self.speed_y

        # 随机改变方向
        if not self.was_thrown and not hit_boundary and random.random() < 0.02:
            # 只有在速度接近正常游走速度时才随机转向
            if abs(self.speed_x) <= abs(self.default_speed_x) * 1.2:
                speed = (abs(self.speed_x) + abs(self.speed_y)) / 2
                self.speed_x = random.choice([-speed, speed])
                self.speed_y = random.choice([-speed, speed])

        # 更新宠物位置
        self.pet_instance.x = new_x
        self.pet_instance.y = new_y

        if hasattr(self.pet_instance, 'update_position'):
            self.pet_instance.update_position(new_x, new_y)
        else:
            self.pet_instance.move(int(new_x), int(new_y))

    def _apply_speed_decay(self):
        """应用速度衰减，慢慢恢复到默认速度"""
        if abs(self.speed_x) > abs(self.default_speed_x) or abs(self.speed_y) > abs(self.default_speed_y):
            self.speed_x *= self.decay_rate
            self.speed_y *= self.decay_rate

            if (abs(self.speed_x) <= abs(self.default_speed_x) * 1.05 and
                abs(self.speed_y) <= abs(self.default_speed_y) * 1.05):
                self.speed_x = self.default_speed_x if self.speed_x > 0 else -self.default_speed_x
                self.speed_y = self.default_speed_y if self.speed_y > 0 else -self.default_speed_y
                self.was_thrown = False

    def _handle_window_collision(self, window_rect, new_x, new_y, pet_width, pet_height):
        """处理与窗口的碰撞（修复闪现：重叠时改为快速移出）"""
        current_x = self.pet_instance.x
        current_y = self.pet_instance.y

        win_left = window_rect.left()
        win_right = window_rect.right()
        win_top = window_rect.top()
        win_bottom = window_rect.bottom()

        # 当前位置边界
        curr_coll_left = current_x + self.collision_margin
        curr_coll_right = current_x + pet_width - self.collision_margin
        curr_coll_top = current_y + self.collision_margin
        curr_coll_bottom = current_y + pet_height - self.collision_margin

        # 下一帧判定边界
        pet_coll_left = new_x + self.collision_margin
        pet_coll_right = new_x + pet_width - self.collision_margin
        pet_coll_top = new_y + self.collision_margin
        pet_coll_bottom = new_y + pet_height - self.collision_margin

        # --- 情况 A: 边缘碰撞反弹 (维持坐标修正) ---
        if curr_coll_right <= win_left and pet_coll_right > win_left:
            self.speed_x = -abs(self.speed_x)
            return (win_left - pet_width + self.collision_margin - 1, new_y)

        if curr_coll_left >= win_right and pet_coll_left < win_right:
            self.speed_x = abs(self.speed_x)
            return (win_right - self.collision_margin + 1, new_y)

        if curr_coll_bottom <= win_top and pet_coll_bottom > win_top:
            self.speed_y = -abs(self.speed_y)
            return (new_x, win_top - pet_height + self.collision_margin - 1)

        if curr_coll_top >= win_bottom and pet_coll_top < win_bottom:
            self.speed_y = abs(self.speed_y)
            return (new_x, win_bottom - self.collision_margin + 1)

        # --- 情况 B: 已经处于重叠状态 (修复闪现：加速跑出去) ---
        # 如果桌宠中心在窗口内，或者大面积重叠
        if (pet_coll_left < win_right and pet_coll_right > win_left and
            pet_coll_top < win_bottom and pet_coll_bottom > win_top):

            # 计算逃逸向量：找到距离最近的出口方向
            dist_to_left = abs(pet_coll_right - win_left)
            dist_to_right = abs(pet_coll_left - win_right)
            dist_to_top = abs(pet_coll_bottom - win_top)
            dist_to_bottom = abs(pet_coll_top - win_bottom)

            min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)

            # 逃逸速度设定为默认速度的 2.5 倍
            escape_speed_x = abs(self.default_speed_x) * 2.5
            escape_speed_y = abs(self.default_speed_y) * 2.5

            if min_dist == dist_to_left:
                self.speed_x = -escape_speed_x
            elif min_dist == dist_to_right:
                self.speed_x = escape_speed_x
            elif min_dist == dist_to_top:
                self.speed_y = -escape_speed_y
            elif min_dist == dist_to_bottom:
                self.speed_y = escape_speed_y

            # 返回 None 意味着不直接修改坐标，让它根据新速度在下一帧自然移出
            return None

        return None

    def set_speed(self, speed_x, speed_y):
        self.speed_x = speed_x
        self.speed_y = speed_y

    def get_position(self):
        return self.pet_instance.x, self.pet_instance.y