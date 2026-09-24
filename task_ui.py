"""
定时任务UI - 支持任务分类
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTimeEdit, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont
import os


class TaskTypeSelector(QDialog):
    """任务类型选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择任务类型")
        self.setMinimumSize(400, 300)

        self.selected_type = "once"
        self.selected_weekday = 0

        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("请选择任务执行方式：")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setStyleSheet("padding: 10px;")
        layout.addWidget(title)

        # 单选按钮组
        self.button_group = QButtonGroup(self)

        # 一次性任务
        self.radio_once = QRadioButton("🔵 一次性任务")
        self.radio_once.setFont(QFont("Microsoft YaHei", 10))
        self.radio_once.setChecked(True)
        self.button_group.addButton(self.radio_once)
        layout.addWidget(self.radio_once)

        desc_once = QLabel("    只在指定时间执行一次，执行后自动禁用")
        desc_once.setFont(QFont("Microsoft YaHei", 9))
        desc_once.setStyleSheet("color: gray; padding-left: 20px;")
        layout.addWidget(desc_once)

        layout.addSpacing(10)

        # 每天重复
        self.radio_daily = QRadioButton("🔁 每天重复")
        self.radio_daily.setFont(QFont("Microsoft YaHei", 10))
        self.button_group.addButton(self.radio_daily)
        layout.addWidget(self.radio_daily)

        desc_daily = QLabel("    每天在指定时间自动执行")
        desc_daily.setFont(QFont("Microsoft YaHei", 9))
        desc_daily.setStyleSheet("color: gray; padding-left: 20px;")
        layout.addWidget(desc_daily)

        layout.addSpacing(10)

        # 每周重复
        self.radio_weekly = QRadioButton("📅 每周重复")
        self.radio_weekly.setFont(QFont("Microsoft YaHei", 10))
        self.button_group.addButton(self.radio_weekly)
        layout.addWidget(self.radio_weekly)

        desc_weekly = QLabel("    每周指定日期在指定时间执行")
        desc_weekly.setFont(QFont("Microsoft YaHei", 9))
        desc_weekly.setStyleSheet("color: gray; padding-left: 20px;")
        layout.addWidget(desc_weekly)

        # 星期选择（仅weekly时启用）
        weekday_layout = QHBoxLayout()
        weekday_layout.addSpacing(40)
        weekday_layout.addWidget(QLabel("选择星期："))

        self.weekday_combo = QComboBox()
        self.weekday_combo.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        self.weekday_combo.setEnabled(False)
        self.weekday_combo.setFont(QFont("Microsoft YaHei", 9))
        weekday_layout.addWidget(self.weekday_combo)
        weekday_layout.addStretch()

        layout.addLayout(weekday_layout)

        # 连接信号
        self.radio_weekly.toggled.connect(self.weekday_combo.setEnabled)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()

        btn_ok = QPushButton("✅ 确定")
        btn_ok.setFont(QFont("Microsoft YaHei", 10))
        btn_ok.clicked.connect(self.accept)

        btn_cancel = QPushButton("❌ 取消")
        btn_cancel.setFont(QFont("Microsoft YaHei", 10))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def get_task_type(self):
        """获取选择的任务类型"""
        if self.radio_once.isChecked():
            return "once", None
        elif self.radio_daily.isChecked():
            return "daily", None
        elif self.radio_weekly.isChecked():
            return "weekly", self.weekday_combo.currentIndex()
        return "once", None


class TaskSetupDialog(QDialog):
    """任务设置对话框 - 完整版"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置定时任务")
        self.setMinimumWidth(450)

        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.task_type = "once"
        self.weekday = None

        layout = QVBoxLayout(self)

        # 文件信息
        file_label = QLabel(f"📁 文件: {self.file_name}")
        file_label.setFont(QFont("Microsoft YaHei", 10))
        file_label.setStyleSheet("padding: 10px; background-color: #F5F5F5; border-radius: 5px;")
        layout.addWidget(file_label)

        # 任务类型选择按钮
        type_btn = QPushButton("🎯 选择任务类型（当前：一次性）")
        type_btn.setFont(QFont("Microsoft YaHei", 10))
        type_btn.clicked.connect(self.select_task_type)
        layout.addWidget(type_btn)

        self.type_display = type_btn

        # 时间选择
        time_layout = QHBoxLayout()
        time_label = QLabel("⏰ 执行时间：")
        time_label.setFont(QFont("Microsoft YaHei", 10))
        time_layout.addWidget(time_label)

        self.time_edit = QTimeEdit(QTime.currentTime().addSecs(60))
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setFont(QFont("Microsoft YaHei", 11))
        self.time_edit.setMinimumHeight(30)
        time_layout.addWidget(self.time_edit)

        layout.addLayout(time_layout)

        # 说明
        hint = QLabel("💡 提示：一次性任务执行后会自动禁用，重复任务会持续执行")
        hint.setFont(QFont("Microsoft YaHei", 9))
        hint.setStyleSheet("color: gray; padding: 10px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 按钮
        btn_layout = QHBoxLayout()

        btn_ok = QPushButton("✅ 添加任务")
        btn_ok.setFont(QFont("Microsoft YaHei", 10))
        btn_ok.clicked.connect(self.accept)

        btn_cancel = QPushButton("❌ 取消")
        btn_cancel.setFont(QFont("Microsoft YaHei", 10))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def select_task_type(self):
        """选择任务类型"""
        dlg = TaskTypeSelector(self)
        if dlg.exec_() == QDialog.Accepted:
            task_type, weekday = dlg.get_task_type()
            self.task_type = task_type
            self.weekday = weekday

            # 更新按钮显示
            type_names = {
                "once": "一次性",
                "daily": "每天重复",
                "weekly": "每周重复"
            }

            text = f"🎯 选择任务类型（当前：{type_names[task_type]}"
            if task_type == "weekly" and weekday is not None:
                weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                text += f" - {weekdays[weekday]}"
            text += "）"

            self.type_display.setText(text)

    def get_task_info(self):
        """获取任务信息"""
        return {
            "name": self.file_name,
            "path": self.file_path,
            "time": self.time_edit.time().toString("HH:mm"),
            "type": self.task_type,
            "weekday": self.weekday
        }


class TaskListDialog(QDialog):
    """任务列表查看对话框"""

    def __init__(self, scheduler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 定时任务列表")
        self.setMinimumSize(600, 400)

        self.scheduler = scheduler

        layout = QVBoxLayout(self)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel(f"当前任务：共 {len(scheduler.tasks)} 个")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_layout.addWidget(title_label)

        # 清理按钮
        btn_clean = QPushButton("🗑️ 清理已完成")
        btn_clean.setFont(QFont("Microsoft YaHei", 9))
        btn_clean.clicked.connect(self.clean_tasks)
        title_layout.addWidget(btn_clean)

        layout.addLayout(title_layout)

        # 图例
        legend = QLabel("图例：✅ 启用 | ⏸️ 已禁用 | 🔵 一次性 | 🔁 每天 | 📅 每周")
        legend.setFont(QFont("Microsoft YaHei", 9))
        legend.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(legend)

        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setFont(QFont("Microsoft YaHei", 10))
        self.refresh_list()
        layout.addWidget(self.task_list)

        # 按钮区
        btn_layout = QHBoxLayout()

        btn_toggle = QPushButton("⏯️ 启用/禁用")
        btn_toggle.clicked.connect(self.toggle_task)

        btn_delete = QPushButton("🗑️ 删除选中")
        btn_delete.clicked.connect(self.delete_task)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)

        btn_layout.addWidget(btn_toggle)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def refresh_list(self):
        """刷新任务列表"""
        self.task_list.clear()

        if not self.scheduler.tasks:
            item = QListWidgetItem("🔭 暂无定时任务")
            item.setFlags(Qt.NoItemFlags)
            self.task_list.addItem(item)
        else:
            for i, task in enumerate(self.scheduler.tasks):
                text = self.scheduler.get_task_display_text(task)
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, i)
                self.task_list.addItem(item)

    def toggle_task(self):
        """启用/禁用任务"""
        item = self.task_list.currentItem()
        if item and item.data(Qt.UserRole) is not None:
            index = item.data(Qt.UserRole)
            self.scheduler.toggle_task(index)
            self.refresh_list()

    def delete_task(self):
        """删除任务"""
        item = self.task_list.currentItem()
        if item and item.data(Qt.UserRole) is not None:
            index = item.data(Qt.UserRole)
            task = self.scheduler.tasks[index]

            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除任务：\n{task['name']}？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.scheduler.remove_task(index)
                self.refresh_list()

    def clean_tasks(self):
        """清理已执行的一次性任务"""
        count = self.scheduler.clean_executed_once_tasks()
        if count > 0:
            QMessageBox.information(self, "清理完成", f"已清理 {count} 个已完成的任务")
            self.refresh_list()
        else:
            QMessageBox.information(self, "无需清理", "没有需要清理的任务")