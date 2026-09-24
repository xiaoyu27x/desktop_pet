"""
汇率提醒模块 - 支持阈值提醒和邮件通知
"""
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox


class ExchangeRateAlerter(QObject):
    """汇率提醒器"""

    # 信号
    alert_triggered = pyqtSignal(dict)  # 提醒触发信号

    def __init__(self):
        super().__init__()

        # 提醒配置
        self.alerts = []  # [{currency_pair, threshold, type, enabled}, ...]

        # 邮件配置
        self.email_config = self._load_email_config()

        # 提醒历史（防止重复提醒）
        self.alert_history = []

        # 声音提醒开关
        self.sound_enabled = True

        print("🔔 汇率提醒器已初始化")

    def _load_email_config(self):
        """加载邮件配置"""
        config_file = ".email_config.json"

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载邮件配置失败: {e}")

        # 默认配置（需要用户填写）
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",  # 发件邮箱
            "sender_password": "",  # 邮箱密码或应用专用密码
            "receiver_email": "",  # 收件邮箱
            "enabled": False
        }

    def save_email_config(self, config):
        """保存邮件配置"""
        try:
            with open(".email_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self.email_config = config
            print("✅ 邮件配置已保存")
            return True

        except Exception as e:
            print(f"❌ 保存邮件配置失败: {e}")
            return False

    def add_alert(self, currency_pair, threshold, alert_type="below"):
        """
        添加提醒

        Args:
            currency_pair: 货币对
            threshold: 阈值
            alert_type: 提醒类型 ("below" 低于, "above" 高于)
        """
        alert = {
            "currency_pair": currency_pair,
            "threshold": threshold,
            "type": alert_type,
            "enabled": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.alerts.append(alert)
        self._save_alerts()

        print(f"🔔 已添加提醒: {currency_pair} {alert_type} {threshold}")

        return alert

    def remove_alert(self, index):
        """移除提醒"""
        if 0 <= index < len(self.alerts):
            removed = self.alerts.pop(index)
            self._save_alerts()
            print(f"🗑️ 已移除提醒: {removed['currency_pair']}")
            return True
        return False

    def check_rate(self, currency_pair, current_rate, pet_instance=None, config_alerts=None):
        """
        检查汇率是否触发提醒

        Args:
            currency_pair: 货币对
            current_rate: 当前汇率
            pet_instance: 桌宠实例（用于动画）
            config_alerts: 从 config 传入的提醒列表（优先使用）
        """
        # 优先用 config 传入的 alerts，否则用 self.alerts
        alerts_to_check = config_alerts if config_alerts is not None else self.alerts

        for alert in alerts_to_check:
            if not alert.get('enabled', True):
                continue

            # 如果 alert 有 currency_pair 字段则校验，否则跳过（config 的 alert 没有此字段）
            if 'currency_pair' in alert and alert['currency_pair'] != currency_pair:
                continue

            threshold = alert['threshold']
            alert_type = alert['type']

            # 检查是否触发
            triggered = False

            if alert_type == "below" and current_rate <= threshold:
                triggered = True
                message = f"汇率低于设定值！\n{currency_pair}: {current_rate:.4f} ≤ {threshold:.4f}"

            elif alert_type == "above" and current_rate >= threshold:
                triggered = True
                message = f"汇率高于设定值！\n{currency_pair}: {current_rate:.4f} ≥ {threshold:.4f}"

            if triggered:
                # 检查是否已经提醒过（5分钟内不重复）
                alert_key = f"{currency_pair}_{alert_type}_{threshold}"

                if not self._is_recently_alerted(alert_key):
                    # 执行提醒
                    self._trigger_alert(message, currency_pair, current_rate, pet_instance)

                    # 记录提醒历史
                    self._add_alert_history(alert_key)

    def _trigger_alert(self, message, currency_pair, rate, pet_instance=None):
        """触发提醒"""
        print(f"🚨 提醒: {message}")
        print(f"🔔 sound_enabled={self.sound_enabled}，即将调用音效")
        print(f"🔔 sound_enabled={self.sound_enabled}，即将调用音效")

        # 1. 发送信号
        self.alert_triggered.emit({
            "message": message,
            "currency_pair": currency_pair,
            "rate": rate,
            "time": datetime.now()
        })

        # 2. 桌宠跳动
        if pet_instance and hasattr(pet_instance, 'animation'):
            pet_instance.animation.stretch_on_click()

        # 3. 声音提醒
        if self.sound_enabled:
            self._play_alert_sound()

    def _play_alert_sound(self):
        """播放提醒声音（子线程，避免阻塞主线程）"""
        import threading
        def _play():
            import os

            # 优先从加密包解密到临时文件
            sound_path = None
            try:
                from resource_loader import res
                sound_path = res.extract_temp("resources/alert.mp3", suffix=".mp3")
                print(f"🔊 从加密包解密音效: {sound_path}")
            except Exception:
                pass

            # 回退到文件系统
            if not sound_path or not os.path.exists(sound_path):
                sound_path = os.path.abspath('resources/alert.mp3')
                print(f"🔊 从文件系统读取音效: {sound_path}")

            if not os.path.exists(sound_path):
                print("⚠️ 找不到 alert.mp3，跳过音效")
                return

            # 方案1：playsound
            try:
                from playsound import playsound
                playsound(sound_path)
                print("✅ playsound 播放成功")
                return
            except Exception as e:
                print(f"⚠️ playsound 失败: {e}")

            # 方案2：Windows Media Player 静默播放
            try:
                import subprocess
                subprocess.Popen(
                    ['powershell', '-c',
                     f'Add-Type -AssemblyName presentationCore;'
                     f'$mp = [System.Windows.Media.MediaPlayer]::new();'
                     f'$mp.Open([Uri]::new("{sound_path}"));'
                     f'$mp.Play();'
                     f'Start-Sleep -s 5'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                print("✅ PowerShell MediaPlayer 播放")
            except Exception as e:
                print(f"⚠️ PowerShell 播放失败: {e}")

        threading.Thread(target=_play, daemon=True).start()

    def _send_email_alert(self, message, currency_pair, rate):
        """发送邮件提醒"""
        if not self.email_config.get('sender_email') or not self.email_config.get('receiver_email'):
            print("⚠️ 邮件配置不完整，跳过邮件提醒")
            return

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = f"汇率提醒：{currency_pair}"

            # 邮件正文
            body = f"""
            汇率提醒通知

            {message}

            当前汇率: {rate:.4f}
            提醒时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            ---
            此邮件由桌面宠物自动发送
            """

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 发送邮件
            server = smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_config['sender_email'],
                self.email_config['sender_password']
            )

            server.send_message(msg)
            server.quit()

            print(f"📧 已发送邮件提醒到: {self.email_config['receiver_email']}")

        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")

    def _is_recently_alerted(self, alert_key, minutes=5):
        """检查是否最近已提醒过"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)

        for item in self.alert_history:
            if item['key'] == alert_key and item['timestamp'] >= cutoff_time:
                return True

        return False

    def _add_alert_history(self, alert_key):
        """添加到提醒历史"""
        self.alert_history.append({
            'key': alert_key,
            'timestamp': datetime.now().timestamp()
        })

        # 只保留最近1小时的历史
        cutoff = datetime.now().timestamp() - 3600
        self.alert_history = [
            item for item in self.alert_history
            if item['timestamp'] >= cutoff
        ]

    def _save_alerts(self):
        """保存提醒配置"""
        try:
            with open("exchange_alerts.json", 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存提醒配置失败: {e}")

    def _load_alerts(self):
        """加载提醒配置"""
        if os.path.exists("exchange_alerts.json"):
            try:
                with open("exchange_alerts.json", 'r', encoding='utf-8') as f:
                    self.alerts = json.load(f)
                print(f"✅ 已加载 {len(self.alerts)} 个提醒")
            except Exception as e:
                print(f"⚠️ 加载提醒配置失败: {e}")

    def get_alerts(self):
        """获取所有提醒"""
        return self.alerts

    def toggle_alert(self, index):
        """切换提醒启用状态"""
        if 0 <= index < len(self.alerts):
            self.alerts[index]['enabled'] = not self.alerts[index]['enabled']
            self._save_alerts()
            return True
        return False