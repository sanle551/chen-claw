"""
推送通知模块
"""
import requests
from typing import Dict

class TelegramNotifier:
    """Telegram 推送器"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_report(self, report: str) -> bool:
        """发送分析报告"""
        try:
            # 如果报告太长，分段发送
            max_length = 4000
            
            if len(report) <= max_length:
                return self._send_message(report)
            else:
                # 分段发送
                parts = [report[i:i+max_length] for i in range(0, len(report), max_length)]
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        part += "\n\n<i>(待续...)</i>"
                    else:
                        part = f"<i>(续 {i+1}/{len(parts)})</i>\n\n" + part
                    
                    if not self._send_message(part):
                        return False
                return True
                
        except Exception as e:
            print(f"发送报告失败: {e}")
            return False
    
    def _send_message(self, text: str) -> bool:
        """发送单条消息"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                print("✅ Telegram 推送成功")
                return True
            else:
                print(f"❌ Telegram API 错误: {result}")
                return False
                
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def send_alert(self, symbol: str, alert_type: str, message: str) -> bool:
        """发送预警"""
        emoji_map = {
            'price_alert': '🚨',
            'stop_loss': '⛔',
            'take_profit': '✅',
            'news': '📰',
            'risk': '⚠️'
        }
        
        emoji = emoji_map.get(alert_type, '📊')
        
        text = f"""{emoji} <b>代币预警 - {symbol}</b>

{message}

时间: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"""
        
        return self._send_message(text)

from datetime import datetime
