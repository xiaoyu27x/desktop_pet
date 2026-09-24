"""
窗口检测模块 - 识别前台窗口
"""
from PyQt5.QtCore import QTimer, QRect
import sys

# 尝试导入平台特定的窗口管理库
try:
    if sys.platform == 'win32':
        import win32gui
        import win32process
        HAS_WIN32 = True
    else:
        HAS_WIN32 = False
except ImportError:
    HAS_WIN32 = False


class WindowDetector:
    def __init__(self, pet_instance):
        self.pet_instance = pet_instance
        self.active_window_rect = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_active_window)
        self.update_interval = 500  # 每500ms更新一次前台窗口

        # 启动检测
        self.update_timer.start(self.update_interval)

    def update_active_window(self):
        """更新当前活动窗口的位置"""
        if HAS_WIN32 and sys.platform == 'win32':
            self._update_windows()
        else:
            # 非 Windows 平台或没有库，禁用此功能
            self.active_window_rect = None

    def _update_windows(self):
        """Windows 平台窗口检测"""
        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()

            if hwnd == 0:
                self.active_window_rect = None
                return

            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)

            # 忽略桌面和自己
            if not title or title == "Program Manager":
                self.active_window_rect = None
                return

            # 检查是否是宠物自己的窗口（多种方式检查）
            if hasattr(self.pet_instance, 'winId'):
                try:
                    # 方式1：直接比较句柄
                    pet_hwnd = int(self.pet_instance.winId())
                    if hwnd == pet_hwnd:
                        self.active_window_rect = None
                        return

                    # 方式2：检查窗口类名（PyQt窗口特征）
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name.startswith('Qt'):
                        # 进一步检查是否是宠物窗口
                        try:
                            # 获取窗口所属进程
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            import os
                            if pid == os.getpid():  # 同一进程
                                self.active_window_rect = None
                                return
                        except:
                            pass
                except:
                    pass

            # 获取窗口位置
            try:
                rect = win32gui.GetWindowRect(hwnd)
                left, top, right, bottom = rect

                # 检查窗口是否最小化或大小为0
                if right - left <= 0 or bottom - top <= 0:
                    self.active_window_rect = None
                    return

                # 保存窗口区域
                self.active_window_rect = QRect(left, top, right - left, bottom - top)

            except Exception as e:
                self.active_window_rect = None

        except Exception as e:
            self.active_window_rect = None

    def get_active_window_rect(self):
        """获取当前活动窗口的矩形区域"""
        return self.active_window_rect

    def is_point_in_window(self, x, y):
        """检查点是否在窗口内"""
        if self.active_window_rect is None:
            return False
        return self.active_window_rect.contains(int(x), int(y))

    def is_rect_intersects_window(self, x, y, width, height):
        """检查矩形是否与窗口相交"""
        if self.active_window_rect is None:
            return False

        pet_rect = QRect(int(x), int(y), width, height)
        return self.active_window_rect.intersects(pet_rect)

    def stop(self):
        """停止检测"""
        self.update_timer.stop()