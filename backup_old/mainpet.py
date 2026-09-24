# import sys
# import random
# import os
# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QLabel, QMenu, QAction,
#     QFileDialog, QDialog, QVBoxLayout, QHBoxLayout,
#     QPushButton, QTimeEdit, QListWidget, QListWidgetItem, QMessageBox
# )
# from PyQt5.QtCore import QTimer, Qt, QTime
# from PyQt5.QtGui import QPixmap, QFont, QCursor
#
# # 导入模块
# from pet_movement import MovementManager
# from pet_animation import AnimationManager
# from pet_interaction import InteractionHandler
# from pet_window_detector import WindowDetector
# from task_managers import TaskHistoryManager, ShortcutManager
# from shortcut_ui import ShortcutDialog
#
# # 导入全局快捷键库
# try:
#     import keyboard
#
#     HAS_KEYBOARD = True
# except ImportError:
#     HAS_KEYBOARD = False
#     print("⚠️ 未安装 keyboard 库，快捷键召唤功能将不可用")
#     print("安装方法: pip install keyboard")
#
#
# class DesktopPet(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # 窗口设置
#         self.setWindowFlags(
#             Qt.FramelessWindowHint |
#             Qt.WindowStaysOnTopHint |
#             Qt.Tool |
#             Qt.X11BypassWindowManagerHint
#         )
#         self.setAttribute(Qt.WA_TranslucentBackground)
#
#         # 基础属性
#         self.pet_width = 140
#         self.pet_height = 140
#         self.x = 0
#         self.y = 0
#         self.resize(self.pet_width, self.pet_height)
#
#         # 初始化位置
#         screen_geometry = QApplication.primaryScreen().geometry()
#         self.x = random.randint(0, screen_geometry.width() - self.pet_width)
#         self.y = random.randint(0, screen_geometry.height() - self.pet_height)
#         self.move(self.x, self.y)
#
#         # 创建标签并加载图片
#         self.pet_label = QLabel(self)
#         self.pet_label.setGeometry(0, 0, self.pet_width, self.pet_height)
#         self.pet_label.setAlignment(Qt.AlignCenter)
#         self.load_pet_image()
#
#         # 报时标签
#         self.time_label = QLabel(self)
#         self.time_label.setGeometry(0, 0, self.pet_width, 30)
#         self.time_label.setAlignment(Qt.AlignCenter)
#         self.time_label.setStyleSheet("""
#             color: #FF5500;
#             font-weight: bold;
#             background-color: rgba(255, 255, 255, 180);
#             border-radius: 5px;
#         """)
#         self.time_label.setFont(QFont("Arial", 12))
#         self.time_label.hide()
#
#         # 创建管理器
#         self.movement = MovementManager(self)
#         self.animation = AnimationManager(self)
#         self.interaction = InteractionHandler(self)
#         self.window_detector = WindowDetector(self)
#
#         # 关键：新增管理器
#         self.history_manager = TaskHistoryManager()
#         self.shortcut_manager = ShortcutManager()
#
#         # 关联窗口检测器
#         self.movement.window_detector = self.window_detector
#
#         # 图片加载后保存原始图片
#         QTimer.singleShot(100, self._save_original_image)
#
#         # 启动移动
#         self.movement.start_moving()
#
#         # 定时任务相关
#         self.scheduled_tasks = []
#         self.last_reported_minute = -1
#
#         self.global_check_timer = QTimer(self)
#         self.global_check_timer.timeout.connect(self.check_time_events)
#         self.global_check_timer.start(1000)
#
#         # 初始化全局快捷键
#         self.current_hotkey = self.shortcut_manager.load_shortcut()
#         if HAS_KEYBOARD:
#             self.register_global_hotkey()
#
#     def _save_original_image(self):
#         """延迟保存原始图片"""
#         if hasattr(self, 'animation'):
#             self.animation.save_original_pixmap()
#
#     def load_pet_image(self):
#         """加载宠物图片"""
#         image_files = ['pet.png', 'pet.jpg', 'pet.gif']
#
#         for image_file in image_files:
#             if os.path.exists(image_file):
#                 pixmap = QPixmap(image_file)
#                 if not pixmap.isNull():
#                     pixmap = pixmap.scaled(
#                         self.pet_width, self.pet_height,
#                         Qt.KeepAspectRatio, Qt.SmoothTransformation
#                     )
#                     self.pet_label.setAlignment(Qt.AlignCenter)
#                     self.pet_label.setPixmap(pixmap)
#                     print(f"✅ 成功加载图片: {image_file}")
#                     return
#
#         print("⚠️ 未找到宠物图片，使用默认占位符")
#         self.create_placeholder()
#
#     def create_placeholder(self):
#         """创建占位符"""
#         from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
#
#         pixmap = QPixmap(self.pet_width, self.pet_height)
#         pixmap.fill(Qt.transparent)
#
#         painter = QPainter(pixmap)
#         painter.setRenderHint(QPainter.Antialiasing)
#         painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
#         painter.setPen(QPen(QColor(50, 100, 200), 2))
#         painter.drawEllipse(10, 10, 120, 120)
#         painter.end()
#
#         self.pet_label.setAlignment(Qt.AlignCenter)
#         self.pet_label.setPixmap(pixmap)
#
#     def check_time_events(self):
#         """时间事件检查逻辑"""
#         now = QTime.currentTime()
#         curr_min = now.minute()
#         curr_sec = now.second()
#
#         # 每分钟报时
#         if curr_min != self.last_reported_minute and curr_sec == 0:
#             self.report_time(now.toString("HH:mm"))
#             self.last_reported_minute = curr_min
#
#         # 定时开启软件检测
#         for task in self.scheduled_tasks[:]:
#             if abs(now.secsTo(task["time"])) <= 1:
#                 success = self.execute_scheduled_task(task)
#                 self.scheduled_tasks.remove(task)
#
#     def execute_scheduled_task(self, task):
#         """执行定时任务并记录历史"""
#         path = task["path"]
#         name = task["name"]
#
#         # 检查路径是否存在
#         if not os.path.exists(path):
#             print(f"❌ 路径不存在: {path}")
#             self.history_manager.record_launch(name, path)
#             QMessageBox.warning(self, "启动失败", f"文件不存在:\n{path}")
#             return False
#
#         # 尝试启动
#         try:
#             os.startfile(path)
#             print(f"✅ 已启动: {name}")
#             self.history_manager.record_launch(name, path)
#             return True
#         except Exception as e:
#             print(f"❌ 启动失败: {e}")
#             self.history_manager.record_launch(name, path)
#             QMessageBox.warning(self, "启动失败", f"无法启动:\n{str(e)}")
#             return False
#
#     def report_time(self, time_str):
#         """显示报时信息并执行动画"""
#         self.time_label.setText(time_str)
#         self.time_label.show()
#
#         if hasattr(self, 'animation') and not self.animation.is_playing:
#             self.animation.stretch_on_click()
#
#         QTimer.singleShot(3000, self.restore_from_report)
#
#     def restore_from_report(self):
#         """恢复状态"""
#         if self.time_label.isVisible():
#             self.time_label.hide()
#
#     # ============ 全局快捷键功能 ============
#
#     def register_global_hotkey(self):
#         """注册全局快捷键"""
#         if not HAS_KEYBOARD:
#             return
#
#         try:
#             # 先清除所有旧的快捷键（使用更安全的方式）
#             try:
#                 keyboard.unhook_all_hotkeys()
#             except:
#                 keyboard.unhook_all()
#
#             # 注册新快捷键（添加 suppress 参数）
#             keyboard.add_hotkey(
#                 self.current_hotkey,
#                 self.summon_to_mouse,
#                 suppress=False,  # 不抑制其他程序
#                 trigger_on_release=False
#             )
#             print(f"✅ 已注册快捷键: {self.current_hotkey}")
#         except AttributeError as e:
#             # 如果是 blocking_hotkeys 错误，尝试备用方法
#             print(f"⚠️ keyboard 库版本不兼容，使用备用方法")
#             try:
#                 # 使用旧版本 API
#                 keyboard.add_hotkey(self.current_hotkey, self.summon_to_mouse)
#                 print(f"✅ 已注册快捷键（备用方法）: {self.current_hotkey}")
#             except Exception as e2:
#                 print(f"❌ 快捷键注册失败: {e2}")
#                 print("💡 建议：以管理员身份运行程序")
#         except Exception as e:
#             print(f"❌ 快捷键注册失败: {e}")
#             print("💡 建议：")
#             print("   1. 以管理员身份运行")
#             print("   2. 或卸载重装 keyboard 库: pip install --upgrade keyboard")
#
#     def summon_to_mouse(self):
#         """召唤到鼠标位置并弹跳"""
#         cursor_pos = QCursor.pos()
#
#         # 计算移动位置（以宠物中心对齐鼠标）
#         target_x = cursor_pos.x() - self.pet_width // 2
#         target_y = cursor_pos.y() - self.pet_height // 2
#
#         # 移动宠物
#         self.update_position(target_x, target_y)
#
#         # 触发弹跳动画
#         if hasattr(self, 'animation') and not self.animation.is_playing:
#             self.animation.stretch_on_click()
#
#         print(f"🐾 召唤到: ({target_x}, {target_y})")
#
#     def open_shortcut_setting(self):
#         """打开快捷键设置对话框"""
#         if not HAS_KEYBOARD:
#             QMessageBox.warning(
#                 self,
#                 "功能不可用",
#                 "未安装 keyboard 库\n\n安装方法:\npip install keyboard"
#             )
#             return
#
#         dlg = ShortcutDialog(self.current_hotkey, self)
#         if dlg.exec_() == QDialog.Accepted:
#             # 保存新快捷键
#             new_key = dlg.current_key
#             self.shortcut_manager.save_shortcut(new_key)
#             self.current_hotkey = new_key
#
#             # 重新注册
#             self.register_global_hotkey()
#
#             QMessageBox.information(
#                 self,
#                 "设置成功",
#                 f"快捷键已更新为:\n{new_key}\n\n现在可以使用此快捷键召唤宠物了！"
#             )
#
#     # ============ 鼠标事件 ============
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.restore_from_report()
#             if hasattr(self, 'interaction'):
#                 self.interaction.handle_mouse_press(event, self)
#
#     def mouseMoveEvent(self, event):
#         if hasattr(self, 'interaction'):
#             self.interaction.handle_mouse_move(event, self)
#
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             if hasattr(self, 'interaction'):
#                 self.interaction.handle_mouse_release(event, self)
#
#     def update_position(self, x, y):
#         """位置更新方法"""
#         self.x = x
#         self.y = y
#         self.move(int(x), int(y))
#
#     def move(self, *args):
#         """重写move方法，确保内部坐标同步"""
#         super().move(*args)
#         if len(args) == 1:
#             self.x = args[0].x()
#             self.y = args[0].y()
#         elif len(args) == 2:
#             self.x = args[0]
#             self.y = args[1]
#
#     # ============ 右键菜单 ============
#
#     def contextMenuEvent(self, event):
#         """右键菜单"""
#         menu = QMenu(self)
#
#         # === 快捷键召唤 ===
#         hotkey_action = QAction("⌨️ 设置召唤快捷键", self)
#         hotkey_action.triggered.connect(self.open_shortcut_setting)
#         menu.addAction(hotkey_action)
#
#         menu.addSeparator()
#
#         # === 定时任务 ===
#         timer_action = QAction("⏰ 定时开启软件", self)
#         timer_action.triggered.connect(self.setup_timer_task)
#         menu.addAction(timer_action)
#
#         view_tasks_action = QAction("📋 查看定时任务", self)
#         view_tasks_action.triggered.connect(self.view_scheduled_tasks)
#         menu.addAction(view_tasks_action)
#
#         # 新增：查看历史记录
#         history_action = QAction("📜 启动历史记录", self)
#         history_action.triggered.connect(self.view_launch_history)
#         menu.addAction(history_action)
#
#         menu.addSeparator()
#
#         # === 窗口避让 ===
#         avoid_window_action = QAction("窗口避让", self)
#         avoid_window_action.setCheckable(True)
#         if hasattr(self, 'window_detector'):
#             avoid_window_action.setChecked(self.window_detector.update_timer.isActive())
#         avoid_window_action.triggered.connect(self.toggle_window_avoidance)
#         menu.addAction(avoid_window_action)
#
#         # === 碰撞距离 ===
#         if hasattr(self, 'movement'):
#             collision_menu = menu.addMenu("碰撞距离")
#             current_margin = self.movement.collision_margin
#
#             current_action = QAction(f"当前: {current_margin}px", self)
#             current_action.setEnabled(False)
#             collision_menu.addAction(current_action)
#             collision_menu.addSeparator()
#
#             for margin, label in [(10, "很近"), (15, "近"), (20, "默认"), (25, "远"), (30, "很远")]:
#                 action = QAction(f"{label} ({margin}px)", self)
#                 action.setCheckable(True)
#                 if margin == current_margin:
#                     action.setChecked(True)
#                 action.triggered.connect(lambda checked, m=margin: self.set_collision_margin(m))
#                 collision_menu.addAction(action)
#
#         menu.addSeparator()
#
#         # === 其他 ===
#         reload_action = QAction("重新加载图片", self)
#         reload_action.triggered.connect(self.load_pet_image)
#         menu.addAction(reload_action)
#
#         menu.addSeparator()
#
#         exit_action = QAction("退出", self)
#         exit_action.triggered.connect(self.close)
#         menu.addAction(exit_action)
#
#         menu.exec_(event.globalPos())
#
#     # ============ 定时任务功能 ============
#
#     def setup_timer_task(self):
#         """设置定时任务"""
#         file_path, _ = QFileDialog.getOpenFileName(
#             self,
#             "选择要定时开启的软件",
#             "",
#             "可执行文件 (*.exe);;所有文件 (*)"
#         )
#         if not file_path:
#             return
#
#         dlg = QDialog(self)
#         dlg.setWindowTitle("设置开启时间")
#         dlg.setMinimumWidth(300)
#         layout = QVBoxLayout()
#
#         file_name = os.path.basename(file_path)
#         layout.addWidget(QLabel(f"文件: {file_name}"))
#
#         time_edit = QTimeEdit(QTime.currentTime().addSecs(60))
#         time_edit.setDisplayFormat("HH:mm")
#         layout.addWidget(QLabel("选择开启时间:"))
#         layout.addWidget(time_edit)
#
#         btn_layout = QHBoxLayout()
#         btn_ok = QPushButton("✅ 确定")
#         btn_cancel = QPushButton("❌ 取消")
#
#         btn_ok.clicked.connect(dlg.accept)
#         btn_cancel.clicked.connect(dlg.reject)
#
#         btn_layout.addWidget(btn_ok)
#         btn_layout.addWidget(btn_cancel)
#         layout.addLayout(btn_layout)
#
#         dlg.setLayout(layout)
#
#         if dlg.exec_() == QDialog.Accepted:
#             self.scheduled_tasks.append({
#                 "time": time_edit.time(),
#                 "path": file_path,
#                 "name": file_name
#             })
#             print(f"✅ 已添加定时任务: {time_edit.time().toString('HH:mm')} 启动 {file_name}")
#
#     def view_scheduled_tasks(self):
#         """查看定时任务列表"""
#         dlg = QDialog(self)
#         dlg.setWindowTitle("📋 定时任务列表")
#         dlg.setMinimumSize(400, 300)
#
#         layout = QVBoxLayout()
#
#         title_label = QLabel("当前定时任务:")
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
#         layout.addWidget(title_label)
#
#         task_list = QListWidget()
#
#         if not self.scheduled_tasks:
#             item = QListWidgetItem("📭 暂无定时任务")
#             item.setFlags(Qt.NoItemFlags)
#             task_list.addItem(item)
#         else:
#             for i, task in enumerate(self.scheduled_tasks):
#                 time_str = task["time"].toString("HH:mm")
#                 task_text = f"⏰ {time_str} - {task['name']}"
#                 item = QListWidgetItem(task_text)
#                 item.setData(Qt.UserRole, i)
#                 task_list.addItem(item)
#
#         layout.addWidget(task_list)
#
#         btn_layout = QHBoxLayout()
#         btn_delete = QPushButton("🗑️ 删除选中")
#         btn_delete.clicked.connect(lambda: self.delete_selected_task(task_list, dlg))
#         btn_close = QPushButton("关闭")
#         btn_close.clicked.connect(dlg.close)
#
#         btn_layout.addWidget(btn_delete)
#         btn_layout.addWidget(btn_close)
#
#         layout.addLayout(btn_layout)
#         dlg.setLayout(layout)
#         dlg.exec_()
#
#     def delete_selected_task(self, task_list, dialog):
#         """删除选中的定时任务"""
#         current_item = task_list.currentItem()
#         if current_item and current_item.data(Qt.UserRole) is not None:
#             task_index = current_item.data(Qt.UserRole)
#             if 0 <= task_index < len(self.scheduled_tasks):
#                 removed_task = self.scheduled_tasks.pop(task_index)
#                 print(f"🗑️ 已删除任务: {removed_task['name']}")
#                 dialog.close()
#                 self.view_scheduled_tasks()
#
#     def view_launch_history(self):
#         """查看启动历史记录"""
#         history = self.history_manager.load_history()
#
#         dlg = QDialog(self)
#         dlg.setWindowTitle("📜 启动历史记录")
#         dlg.setMinimumSize(600, 400)
#
#         layout = QVBoxLayout()
#
#         title_label = QLabel(f"共 {len(history)} 条记录")
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
#         layout.addWidget(title_label)
#
#         history_list = QListWidget()
#
#         if not history:
#             item = QListWidgetItem("📭 暂无历史记录")
#             item.setFlags(Qt.NoItemFlags)
#             history_list.addItem(item)
#         else:
#             # 倒序显示（最新的在上面）
#             for record in reversed(history):
#                 time_str = record.get("时间", "未知")
#                 name = record.get("任务名", "未知")
#                 status = record.get("执行状态", "未知")
#
#                 # 根据状态设置图标
#                 icon = "✅" if status == "成功" else "❌"
#                 text = f"{icon} {time_str} | {name} | {status}"
#
#                 item = QListWidgetItem(text)
#                 history_list.addItem(item)
#
#         layout.addWidget(history_list)
#
#         btn_layout = QHBoxLayout()
#         btn_clear = QPushButton("🗑️ 清空历史")
#         btn_clear.clicked.connect(lambda: self.clear_history(dlg))
#         btn_close = QPushButton("关闭")
#         btn_close.clicked.connect(dlg.close)
#
#         btn_layout.addWidget(btn_clear)
#         btn_layout.addWidget(btn_close)
#
#         layout.addLayout(btn_layout)
#         dlg.setLayout(layout)
#         dlg.exec_()
#
#     def clear_history(self, dialog):
#         """清空历史记录"""
#         reply = QMessageBox.question(
#             self,
#             "确认清空",
#             "确定要清空所有历史记录吗？",
#             QMessageBox.Yes | QMessageBox.No
#         )
#
#         if reply == QMessageBox.Yes:
#             # 删除历史文件
#             if os.path.exists("task_history.json"):
#                 os.remove("task_history.json")
#             print("🗑️ 已清空历史记录")
#             dialog.close()
#             self.view_launch_history()
#
#     # ============ 其他功能 ============
#
#     def set_collision_margin(self, margin):
#         """设置碰撞边距"""
#         if hasattr(self, 'movement'):
#             self.movement.collision_margin = margin
#             print(f"碰撞边距已设置为: {margin}px")
#
#     def toggle_window_avoidance(self):
#         """开关窗口避让功能"""
#         if hasattr(self, 'window_detector'):
#             if self.window_detector.update_timer.isActive():
#                 self.window_detector.update_timer.stop()
#                 self.window_detector.active_window_rect = None
#             else:
#                 self.window_detector.update_timer.start(500)
#
#     def closeEvent(self, event):
#         """关闭事件"""
#         # 清理快捷键（使用更安全的方式）
#         if HAS_KEYBOARD:
#             try:
#                 keyboard.unhook_all_hotkeys()
#             except:
#                 try:
#                     keyboard.unhook_all()
#                 except:
#                     pass  # 忽略清理错误
#
#         # 停止所有定时器
#         if hasattr(self, 'movement'):
#             self.movement.stop_moving()
#         if hasattr(self, 'window_detector'):
#             self.window_detector.stop()
#         if hasattr(self, 'global_check_timer'):
#             self.global_check_timer.stop()
#
#         event.accept()
#
#
# def main():
#     app = QApplication(sys.argv)
#     pet = DesktopPet()
#     pet.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == "__main__":
#     main()