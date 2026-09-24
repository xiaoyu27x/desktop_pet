# 🐾 DeskPet / 桌宠

> A lightweight desktop companion that lives on your screen — with exchange rate alerts, Pomodoro timer, music player, and more.
>
> 住在你桌面上的小伙伴，支持汇率监控、番茄钟、音乐播放器等实用功能。

<p align="center">
  <img src="docs/preview.gif" alt="DeskPet preview" width="500"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.2-brightgreen" />
  <img src="https://img.shields.io/badge/Platform-Windows-blue?logo=windows" />
  <img src="https://img.shields.io/badge/Python-3.8+-yellow?logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-orange" />
</p>

---

## ⬇️ Download / 下载

**👉 [Releases](https://github.com/Zephyr-34404/deskpet/releases/latest)** — 下载 `.exe`，无需安装 Python，双击即用。

Download the `.exe` from Releases — no Python needed, just double-click and run.

---

## ✨ Features / 功能

| | Feature | 功能 |
|--|---------|------|
| 🐾 | Animated pet roaming your desktop | 在桌面自由游走的动画宠物 |
| 🖱️ | Drag & throw with physics bounce | 拖拽投掷，物理弹跳 |
| 💱 | Live exchange rate monitor (CNY) | 实时汇率监控（人民币基准） |
| 🔔 | Price threshold alerts with sound | 汇率阈值提醒，带音效 |
| 📊 | Export rate history to Excel | 导出汇率历史到 Excel（含折线图） |
| 🍅 | Pomodoro timer with floating overlay | 番茄钟，浮动倒计时 |
| 🎵 | Built-in music player | 内置音乐播放器，支持本地曲库 |
| ⏰ | Task scheduler — one-off / daily / weekly | 定时任务，支持一次性/每天/每周 |
| ⌨️ | Global hotkey to summon pet | 全局快捷键一键召唤宠物 |
| 🪟 | Auto window-avoidance | 自动检测窗口，宠物主动避让 |

---

## 🚀 Getting Started / 快速开始

### 普通用户 / End Users

前往 **[Releases](https://github.com/Zephyr-34404/deskpet/releases/latest)** 下载最新 `DeskPet.exe`，双击运行即可。  
**右键宠物** 打开功能菜单，所有功能都在里面。

Download `DeskPet.exe` from **[Releases](https://github.com/Zephyr-34404/deskpet/releases/latest)** and double-click to run.  
**Right-click the pet** to access all features.

---

### 开发者 / Developers

```bash
git clone https://github.com/Zephyr-34404/deskpet.git
cd deskpet
pip install -r requirements.txt
python mainpet.py
```

> ⚠️ 内置素材（宠物图片、音效、音乐）已加密打包，不随源码发布。  
> 开发时需自备 `resources/` 目录，并运行 `python pack_resources.py` 生成 `resources.dat`。
>
> ⚠️ Bundled assets (sprites, sounds, music) are encrypted and not included in this repo.  
> You'll need to provide your own `resources/` folder and run `python pack_resources.py`.

---

## 🎮 Usage / 使用说明

### 基本操作

| 操作 | 效果 |
|------|------|
| 左键单击 | 弹跳动画 |
| 拖拽后松手 | 投掷宠物，物理滑行 |
| 右键 | 打开功能菜单 |
| 全局快捷键 | 宠物瞬移到鼠标位置 |

### 汇率监控

1. 右键 → **显示汇率** 打开组件（首次打开时联网获取数据）
2. 点击 💰 添加货币对，如 USD/CNY
3. 点击 🔔 设置高/低价提醒阈值
4. 触发时播放音效 + 宠物跳动

### 番茄钟

1. 右键 → **番茄钟** → 设置工作/休息时长
2. 倒计时浮动显示在宠物上方
3. 每轮结束时宠物有庆祝动画

### 音乐播放器

1. 右键 → **音乐播放器**
2. **添加文件夹** 导入本地音乐库
3. 支持随机播放 / 顺序循环
4. 添加过的文件夹会被记住，下次自动同步新增曲目

### 定时任务

1. 右键 → **定时开启软件**
2. 选择要定时启动的程序
3. 设置触发类型：
   - 🔵 **一次性** — 执行后自动禁用
   - 🔁 **每天重复** — 固定时间每天触发
   - 📅 **每周重复** — 指定星期几触发
4. 右键 → **查看定时任务** 管理所有任务

---

## ⚙️ Configuration / 配置

所有配置自动保存，重启后保持：

| 文件 | 内容 |
|------|------|
| `settings.json` | 碰撞距离、窗口避让、快捷键 |
| `exchange_config.json` | 货币对、提醒阈值 |
| `music_playlist.json` | 播放列表、已添加文件夹 |
| `scheduled_tasks_v2.json` | 定时任务列表 |

---

## 📦 Dependencies / 依赖

```
PyQt5>=5.15
requests
beautifulsoup4
pandas
openpyxl
cryptography
playsound
keyboard
pywin32
Pillow
```

```bash
pip install -r requirements.txt
```

---

## 🗂️ Project Structure / 项目结构

```
deskpet/
├── mainpet.py                  # 入口
├── resource_loader.py          # 加密资源加载器
│
├── pet_movement.py             # 移动与物理引擎
├── pet_animation.py            # 挤压拉伸动画
├── pet_interaction.py          # 鼠标交互
├── pet_window_detector.py      # 窗口碰撞检测
│
├── pomodoro_timer.py / ui      # 番茄钟
├── time_display.py             # 报时组件
├── music_player.py / ui        # 音乐播放器
├── task_scheduler.py / ui      # 定时任务
│
├── exchange_rate_*.py          # 汇率模块（抓取/存储/提醒/设置）
├── shortcut_ui.py              # 快捷键录制
├── tray_manager.py             # 系统托盘
├── settings_manager.py         # 配置管理
│
└── resources.dat               # 加密资源包（不进 git）
```

---

## 📝 Changelog / 更新日志

### v3.2 (2026-03-07)
- 🐛 修复番茄钟不显示在最顶层的问题
- 🐛 修复汇率不显示及提醒不触发的问题
- ✨ 拖拽行为优化，移除双击暂停避免冲突
- 🔒 资源文件加密打包（图片、音效、音乐）
- ⚡ 汇率模块改为懒加载，启动不再自动联网

### v3.0 – v3.1 (2026-01-20 – 2026-02-03)
- ✨ 新增系统托盘图标 + 隐藏/显示功能
- ✨ 番茄钟功能（浮动倒计时显示）
- ✨ 音乐播放器（内置默认曲库）
- ✨ 汇率监控小组件（中国银行数据源）
- ✨ 汇率提醒 + 测试功能
- ✨ 隐藏报时功能
- ✨ 重启功能
- 🐛 修复汇率版本回退问题
- 🐛 优化报时与番茄钟位置冲突

### v2.0 (2026-01-21)
- ✨ 新增系统托盘
- ✨ 新增番茄钟（初版）
- 🐛 番茄钟显示异常多轮修复

### v1.0 (2026-01-07 – 2026-01-20)
- 🎉 桌宠本体、右键菜单、点按动画、拖拽效果
- ✨ 定时启动其他软件
- ✨ 报时功能
- ✨ 窗口避让 + 碰撞距离自定义
- ✨ 全局快捷键召唤
- ✨ 定时任务分类（一次性/每天/每周）
- ✨ 配置自动记忆（快捷键、碰撞距离、窗口避让）

---

## 🗺️ Roadmap / 计划中

- [ ] 多语言
- [ ] macOS 支持
- [ ] 插件系统 / Plugin system

---

## 👤 About / 关于作者

Made by **[Zephyr-34404](https://github.com/Zephyr-34404)** — CS student & solo developer.  
This project is part of my personal portfolio, built from scratch with PyQt5.

---

## 📄 License / 许可证

**Code / 代码：** [MIT License](LICENSE) — 可自由 fork 和修改。

**Assets / 素材**（图片、音效、音乐）：All rights reserved. Not for redistribution.  
版权保留，不可二次分发。