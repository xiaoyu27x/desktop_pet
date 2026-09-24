"""
定时任务分类管理系统
支持：一次性任务、每天重复、每周重复
"""
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import QTime


class TaskScheduler:
    """任务调度器 - 支持多种任务类型"""

    TASK_TYPES = {
        "once": "一次性",
        "daily": "每天重复",
        "weekly": "每周重复"
    }

    def __init__(self, filename="scheduled_tasks_v2.json"):
        self.filename = filename
        self.tasks = self.load_tasks()
        self.executed_today = set()  # 记录今天已执行的每日任务

    def load_tasks(self):
        """加载任务列表"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载任务失败: {e}")
                return []
        return []

    def save_tasks(self):
        """保存任务列表"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
            print(f"✅ 已保存 {len(self.tasks)} 个任务")
            return True
        except Exception as e:
            print(f"❌ 保存任务失败: {e}")
            return False

    def add_task(self, name, path, time_str, task_type="once", weekday=None):
        """
        添加任务

        Args:
            name: 任务名称
            path: 程序路径
            time_str: 时间 "HH:MM"
            task_type: 任务类型 "once"/"daily"/"weekly"
            weekday: 星期几 (0-6, 0=周一, 仅weekly类型需要)
        """
        task = {
            "name": name,
            "path": path,
            "time": time_str,
            "type": task_type,
            "enabled": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if task_type == "weekly" and weekday is not None:
            task["weekday"] = weekday

        self.tasks.append(task)
        self.save_tasks()
        return True

    def remove_task(self, index):
        """删除任务"""
        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            self.save_tasks()
            return removed
        return None

    def toggle_task(self, index):
        """启用/禁用任务"""
        if 0 <= index < len(self.tasks):
            self.tasks[index]["enabled"] = not self.tasks[index].get("enabled", True)
            self.save_tasks()
            return True
        return False

    def get_pending_tasks(self, current_time):
        """
        获取当前应该执行的任务

        Args:
            current_time: QTime对象

        Returns:
            待执行任务列表
        """
        pending = []
        current_hour = current_time.hour()
        current_minute = current_time.minute()
        current_weekday = datetime.now().weekday()  # 0=周一, 6=周日
        today_str = datetime.now().strftime("%Y-%m-%d")

        for i, task in enumerate(self.tasks):
            if not task.get("enabled", True):
                continue

            # 解析任务时间
            try:
                task_hour, task_minute = map(int, task["time"].split(":"))
            except:
                continue

            # 时间不匹配则跳过
            if task_hour != current_hour or task_minute != current_minute:
                continue

            task_type = task.get("type", "once")

            # 一次性任务
            if task_type == "once":
                # 检查是否今天已执行
                last_exec = task.get("last_executed")
                if last_exec and last_exec.startswith(today_str):
                    continue
                pending.append((i, task))

            # 每天重复任务
            elif task_type == "daily":
                # 使用集合防止同一天多次执行
                task_id = f"daily_{i}_{today_str}"
                if task_id not in self.executed_today:
                    pending.append((i, task))
                    self.executed_today.add(task_id)

            # 每周重复任务
            elif task_type == "weekly":
                task_weekday = task.get("weekday")
                if task_weekday == current_weekday:
                    task_id = f"weekly_{i}_{today_str}"
                    if task_id not in self.executed_today:
                        pending.append((i, task))
                        self.executed_today.add(task_id)

        return pending

    def mark_executed(self, index):
        """标记任务为已执行"""
        if 0 <= index < len(self.tasks):
            self.tasks[index]["last_executed"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 一次性任务执行后自动禁用
            if self.tasks[index].get("type") == "once":
                self.tasks[index]["enabled"] = False

            self.save_tasks()
            return True
        return False

    def get_task_display_text(self, task):
        """获取任务的显示文本"""
        time_str = task["time"]
        name = task["name"]
        task_type = task.get("type", "once")
        enabled = task.get("enabled", True)

        # 任务类型图标
        type_icon = {
            "once": "🔵",
            "daily": "🔁",
            "weekly": "📅"
        }.get(task_type, "⚪")

        # 启用状态
        status_icon = "✅" if enabled else "⏸️"

        # 星期显示（仅weekly）
        weekday_str = ""
        if task_type == "weekly":
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            wd = task.get("weekday", 0)
            weekday_str = f" ({weekdays[wd]})"

        # 类型说明
        type_name = self.TASK_TYPES.get(task_type, "未知")

        return f"{status_icon} {type_icon} {time_str} - {name} [{type_name}]{weekday_str}"

    def clean_executed_once_tasks(self):
        """清理已执行的一次性任务"""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if not (
                t.get("type") == "once" and not t.get("enabled", True)
        )]
        removed_count = original_count - len(self.tasks)
        if removed_count > 0:
            self.save_tasks()
            print(f"🗑️ 已清理 {removed_count} 个已执行的一次性任务")
        return removed_count