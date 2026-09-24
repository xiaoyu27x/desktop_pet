import json
import os
from datetime import datetime


class TaskHistoryManager:
    """处理任务启动历史记录"""

    def __init__(self, filename="task_history.json"):
        self.filename = filename

    def record_launch(self, task_name, path):
        history = self.load_history()
        # 增加路径存在性判断
        status = "成功" if os.path.exists(path) else "失败 (路径不存在)"

        record = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "任务名": task_name,
            "路径": path,
            "执行状态": status
        }
        history.append(record)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        return os.path.exists(path)

    def load_history(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


class ShortcutManager:
    """处理快捷键配置"""

    def __init__(self, filename="shortcut_config.json"):
        self.filename = filename
        self.default_key = "ctrl+shift+a"

    def save_shortcut(self, key_string):
        with open(self.filename, 'w') as f:
            json.dump({"shortcut": key_string}, f)

    def load_shortcut(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f).get("shortcut", self.default_key)
            except:
                pass
        return self.default_key