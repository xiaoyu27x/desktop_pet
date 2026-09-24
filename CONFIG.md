# 配置文件说明

## 📁 配置文件列表

### 1. `settings.json` - 主配置文件
**自动生成**，包含用户的个人设置

```json
{
    "window_avoidance_enabled": false,  // 窗口避让是否开启
    "collision_margin": 20,             // 碰撞边距（像素）
    "current_hotkey": "ctrl+shift+a",   // 快捷键
    "report_time_enabled": true         // 是否启用报时
}
```

**配置项说明：**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `window_avoidance_enabled` | boolean | `false` | 窗口避让功能开关 |
| `collision_margin` | number | `20` | 碰撞判定边距（10-30像素） |
| `current_hotkey` | string | `"ctrl+shift+a"` | 召唤快捷键 |
| `report_time_enabled` | boolean | `true` | 报时功能开关 |

---

### 2. `shortcut_config.json` - 快捷键配置
**自动生成**，存储快捷键设置（与 settings.json 重复，待合并）

```json
{
    "shortcut": "ctrl+shift+a"
}
```

---

### 3. `scheduled_tasks_v2.json` - 定时任务配置
**自动生成**，包含所有定时任务

```json
[
    {
        "name": "notepad.exe",
        "path": "C:\\Windows\\System32\\notepad.exe",
        "time": "09:00",
        "type": "daily",
        "enabled": true,
        "created_at": "2026-01-19 15:30:00",
        "last_executed": "2026-01-19 09:00:00"
    }
]
```

**任务字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 任务名称 |
| `path` | string | 程序完整路径 |
| `time` | string | 执行时间（HH:MM） |
| `type` | string | 任务类型：`once`/`daily`/`weekly` |
| `enabled` | boolean | 是否启用 |
| `weekday` | number | 星期几（0-6，仅weekly类型） |
| `created_at` | string | 创建时间 |
| `last_executed` | string | 上次执行时间 |

---

### 4. `task_history.json` - 任务执行历史
**自动生成**，记录所有任务执行历史

```json
[
    {
        "时间": "2026-01-19 09:00:00",
        "任务名": "notepad.exe",
        "路径": "C:\\Windows\\System32\\notepad.exe",
        "执行状态": "成功"
    }
]
```

---

## 🔧 配置管理

### 自动保存时机

程序会在以下情况自动保存配置：

1. **碰撞距离调整后** → 立即保存到 `settings.json`
2. **窗口避让开关切换后** → 立即保存到 `settings.json`
3. **快捷键修改后** → 保存到 `settings.json` 和 `shortcut_config.json`
4. **定时任务添加/删除/修改后** → 保存到 `scheduled_tasks_v2.json`
5. **任务执行后** → 添加记录到 `task_history.json`

### 自动加载时机

程序启动时会自动加载：

1. `settings.json` → 恢复窗口避让、碰撞距离等设置
2. `scheduled_tasks_v2.json` → 加载所有定时任务
3. 控制台会显示加载信息

**示例输出：**
```
✅ 已加载碰撞边距设置: 25px
✅ 已启用窗口避让功能
✅ 已加载 3 个定时任务
```

---

## 📝 Git 管理

### 已加入 `.gitignore`

以下文件**不会**被提交到 Git：

```
settings.json
shortcut_config.json
task_history.json
scheduled_tasks.json
scheduled_tasks_v2.json
```

### 示例配置文件

项目提供了示例配置文件 `settings.example.json`：

```bash
# 首次使用时，复制示例文件
cp settings.example.json settings.json
```

---

## ⚙️ 手动修改配置

### 方法 1：通过 UI 修改（推荐）

- 右键菜单 → "碰撞距离" → 选择距离
- 右键菜单 → "窗口避让" → 勾选开关
- 右键菜单 → "⌨️ 设置召唤快捷键" → 录制新快捷键

### 方法 2：直接编辑文件

1. 关闭程序
2. 用文本编辑器打开 `settings.json`
3. 修改配置项
4. 保存文件
5. 重新启动程序

**注意：** 请确保 JSON 格式正确，否则配置会被重置为默认值

---

## 🔄 配置重置

### 重置所有设置

删除配置文件即可：

```bash
# Windows PowerShell
Remove-Item settings.json, shortcut_config.json

# 或者手动删除这些文件
```

程序下次启动时会自动创建默认配置。

### 重置任务数据

```bash
# 清空任务历史
Remove-Item task_history.json

# 清空定时任务
Remove-Item scheduled_tasks_v2.json
```

### 重置单个配置

打开 `settings.json`，删除对应行或修改为默认值：

```json
{
    "window_avoidance_enabled": false,  // 改为 false 关闭窗口避让
    "collision_margin": 20              // 改为 20 恢复默认边距
}
```

---

## 🐛 常见问题

### Q1: 配置没有保存？

**检查：**
1. 程序是否有写入权限
2. 控制台是否显示 "✅ 配置已保存" 信息
3. `settings.json` 文件是否存在

### Q2: 程序启动时配置丢失？

**可能原因：**
- `settings.json` 格式错误被重置
- 文件被删除

**解决方案：**
- 从 `settings.example.json` 复制一份新的

### Q3: 窗口避让设置无效？

**检查：**
1. 是否安装了 `pywin32` 库
2. 控制台是否显示加载信息
3. 手动切换一次窗口避让开关

### Q4: 快捷键设置丢失？

**说明：**
- 快捷键同时保存在两个文件中
- 优先读取 `settings.json`
- 如果 `settings.json` 中没有，读取 `shortcut_config.json`

---

## 📊 配置文件优先级

当多个配置文件存在时：

1. **快捷键：** `settings.json` > `shortcut_config.json` > 默认值
2. **任务：** `scheduled_tasks_v2.json` > `scheduled_tasks.json`（旧版）
3. **其他设置：** `settings.json` > 默认值

---

**最后更新：** 2026-01-19