"""
番茄钟计时器逻辑模块
文件名: pomodoro_timer.py
位置: 项目根目录
"""

from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class PomodoroTimer(QObject):
    """番茄钟计时器"""

    # 信号
    time_updated = pyqtSignal(int, bool)  # (剩余秒数, 是否休息中)
    timer_completed = pyqtSignal()  # 计时完成
    break_completed = pyqtSignal()  # 休息完成
    round_changed = pyqtSignal(int, int)  # (当前轮数, 总轮数)

    def __init__(self):
        """初始化番茄钟"""
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        # 配置参数
        self.work_minutes = 25  # 工作时长
        self.break_minutes = 5  # 休息时长
        self.total_rounds = 1  # 总轮数
        self.is_repeat = False  # 是否重复

        # 运行状态
        self.remaining_seconds = 0  # 剩余秒数
        self.current_round = 0  # 当前轮数
        self.is_break = False  # 是否在休息
        self.is_running = False  # 是否运行中

    def start_timer(self, work_minutes=25, break_minutes=5, rounds=1, is_repeat=False):
        """
        开始计时

        Args:
            work_minutes: 工作时长（分钟）
            break_minutes: 休息时长（分钟）
            rounds: 总轮数
            is_repeat: 是否重复
        """
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.total_rounds = rounds
        self.is_repeat = is_repeat

        # 重置状态
        self.current_round = 1
        self.is_break = False
        self.remaining_seconds = work_minutes * 60
        self.is_running = True

        # 发送初始信号
        self.round_changed.emit(self.current_round, self.total_rounds)
        self.time_updated.emit(self.remaining_seconds, self.is_break)

        # 启动定时器
        self.timer.start(1000)  # 每秒触发一次

        print(f"🍅 番茄钟已启动: {work_minutes}分钟工作 / {break_minutes}分钟休息 / {rounds}轮")

    def stop_timer(self):
        """停止计时"""
        self.timer.stop()
        self.is_running = False
        print("⏹️ 番茄钟已停止")

    def pause_timer(self):
        """暂停计时"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            print("⏸️ 番茄钟已暂停")

    def resume_timer(self):
        """恢复计时"""
        if not self.is_running and self.remaining_seconds > 0:
            self.timer.start(1000)
            self.is_running = True
            print("▶️ 番茄钟已恢复")

    def _tick(self):
        """每秒倒计时逻辑"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_updated.emit(self.remaining_seconds, self.is_break)
        else:
            # 时间到了
            self._handle_time_up()

    def _handle_time_up(self):
        """处理时间到"""
        if self.is_break:
            # 休息结束
            print(f"☕ 休息结束！开始第 {self.current_round + 1} 轮")
            self.break_completed.emit()

            # 检查是否还有下一轮
            if self.current_round < self.total_rounds:
                # 开始下一轮工作
                self.current_round += 1
                self.is_break = False
                self.remaining_seconds = self.work_minutes * 60

                self.round_changed.emit(self.current_round, self.total_rounds)
                self.time_updated.emit(self.remaining_seconds, self.is_break)
            else:
                # 所有轮次完成
                self._all_rounds_completed()
        else:
            # 工作结束
            print(f"🎉 第 {self.current_round} 轮工作完成！")
            self.timer_completed.emit()

            # 检查是否需要休息
            if self.current_round < self.total_rounds or self.is_repeat:
                # 开始休息
                self.is_break = True
                self.remaining_seconds = self.break_minutes * 60
                self.time_updated.emit(self.remaining_seconds, self.is_break)
            else:
                # 最后一轮完成，不需要休息
                self._all_rounds_completed()

    def _all_rounds_completed(self):
        """所有轮次完成"""
        print(f"🎊 所有番茄钟完成！共 {self.current_round} 轮")
        self.timer.stop()
        self.is_running = False

        if self.is_repeat:
            # 重新开始
            print("🔄 重复模式：重新开始")
            self.start_timer(
                self.work_minutes,
                self.break_minutes,
                self.total_rounds,
                self.is_repeat
            )
        else:
            # 完全结束
            self.timer_completed.emit()

    def get_remaining_time(self):
        """
        获取剩余时间

        Returns:
            dict: {"hours": int, "minutes": int, "seconds": int}
        """
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        return {
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }

    def get_status(self):
        """
        获取当前状态

        Returns:
            dict: 状态信息
        """
        return {
            "is_running": self.is_running,
            "is_break": self.is_break,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "remaining_seconds": self.remaining_seconds,
            "work_minutes": self.work_minutes,
            "break_minutes": self.break_minutes
        }