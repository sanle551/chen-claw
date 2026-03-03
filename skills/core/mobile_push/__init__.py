"""
📱 移动端推送技能
PWA支持 + Web Push API + 移动端适配
"""
import json
import base64
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
import os

LOGGER = logging.getLogger("mobile_push")

class MobilePushManager:
    """移动端推送管理器"""
    
    def __init__(self):
        self.subscriptions: List[Dict] = []
        self.vapid_keys = self._generate_or_load_vapid_keys()
        self.push_handlers: Dict[str, Callable] = {}
        
    def _generate_or_load_vapid_keys(self) -> Dict:
        """生成或加载VAPID密钥 (用于Web Push)"""
        # 在实际生产环境中应该使用安全的密钥存储
        return {
            "public_key": "BEl62i...",  # 替换为实际的VAPID公钥
            "private_key": "Xh_..."     # 替换为实际的VAPID私钥
        }
        
    def register_subscription(self, subscription: Dict, user_id: str = None) -> str:
        """注册推送订阅
        
        Args:
            subscription: Web Push订阅对象
            user_id: 可选的用户ID
            
        Returns:
            subscription_id: 订阅ID
        """
        sub_id = f"sub_{int(datetime.now().timestamp())}"
        
        sub_data = {
            "id": sub_id,
            "subscription": subscription,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "platform": self._detect_platform(subscription),
            "enabled": True
        }
        
        self.subscriptions.append(sub_data)
        LOGGER.info(f"注册推送订阅: {sub_id}, 平台: {sub_data['platform']}")
        return sub_id
        
    def unregister_subscription(self, sub_id: str):
        """取消订阅"""
        self.subscriptions = [s for s in self.subscriptions if s["id"] != sub_id]
        LOGGER.info(f"取消推送订阅: {sub_id}")
        
    def _detect_platform(self, subscription: Dict) -> str:
        """检测平台类型"""
        endpoint = subscription.get("endpoint", "")
        
        if "googleapis.com" in endpoint or "fcm.googleapis.com" in endpoint:
            return "android"
        elif "apple.com" in endpoint or "push.apple.com" in endpoint:
            return "ios"
        elif "windows.com" in endpoint:
            return "windows"
        else:
            return "web"
            
    def send_push(self, title: str, body: str, 
                  icon: str = None, 
                  image: str = None,
                  badge: str = None,
                  data: Dict = None,
                  actions: List[Dict] = None,
                  require_interaction: bool = False,
                  silent: bool = False):
        """发送推送通知
        
        Args:
            title: 通知标题
            body: 通知内容
            icon: 图标URL
            image: 大图URL
            badge: 角标图标
            data: 自定义数据
            actions: 操作按钮 [{"action": "open", "title": "打开"}]
            require_interaction: 是否需要用户交互
            silent: 是否静默
        """
        notification = {
            "title": title,
            "body": body,
            "icon": icon or "/static/icon-192x192.png",
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        if image:
            notification["image"] = image
        if badge:
            notification["badge"] = badge
        if data:
            notification["data"] = data
        if actions:
            notification["actions"] = actions
        if require_interaction:
            notification["requireInteraction"] = True
        if silent:
            notification["silent"] = True
            
        # 发送到所有订阅
        success_count = 0
        for sub in self.subscriptions:
            if not sub.get("enabled"):
                continue
                
            try:
                self._send_to_subscription(sub, notification)
                success_count += 1
            except Exception as e:
                LOGGER.error(f"推送失败 {sub['id']}: {e}")
                
        LOGGER.info(f"推送完成: {success_count}/{len(self.subscriptions)}")
        return success_count
        
    def _send_to_subscription(self, subscription: Dict, notification: Dict):
        """发送到单个订阅"""
        # 这里应该使用 pywebpush 或类似库
        # 示例代码结构：
        
        try:
            # from pywebpush import webpush
            # webpush(
            #     subscription_info=subscription["subscription"],
            #     data=json.dumps(notification),
            #     vapid_private_key=self.vapid_keys["private_key"],
            #     vapid_claims={"sub": "mailto:admin@example.com"}
            # )
            LOGGER.debug(f"发送到: {subscription['id']}")
        except Exception as e:
            LOGGER.error(f"发送失败: {e}")
            raise
            
    def send_price_alert(self, symbol: str, price: float, change_pct: float):
        """发送价格预警推送"""
        direction = "📈" if change_pct > 0 else "📉"
        title = f"{direction} {symbol} 价格预警"
        body = f"当前价格: ${price:,.2f} ({change_pct:+.2f}%)"
        
        actions = [
            {"action": "view", "title": "查看详情"},
            {"action": "dismiss", "title": "忽略"}
        ]
        
        self.send_push(
            title=title,
            body=body,
            data={"type": "price_alert", "symbol": symbol, "price": price},
            actions=actions
        )
        
    def send_analysis_complete(self, symbols: List[str]):
        """发送分析完成通知"""
        title = "✅ 每日分析完成"
        body = f"已完成 {len(symbols)} 个代币的分析，点击查看报告"
        
        self.send_push(
            title=title,
            body=body,
            data={"type": "analysis_complete", "symbols": symbols},
            actions=[{"action": "view_report", "title": "查看报告"}]
        )


class PWAConfig:
    """PWA配置生成器"""
    
    @staticmethod
    def generate_manifest(app_name: str = "Crypto Analyzer", 
                         short_name: str = "Crypto",
                         theme_color: str = "#0f1419",
                         background_color: str = "#1a1f2e") -> Dict:
        """生成Web App Manifest"""
        return {
            "name": app_name,
            "short_name": short_name,
            "description": "加密货币智能分析系统",
            "start_url": "/",
            "display": "standalone",
            "background_color": background_color,
            "theme_color": theme_color,
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png"
                },
                {
                    "src": "/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        
    @staticmethod
    def generate_service_worker() -> str:
        """生成Service Worker代码"""
        return '''
const CACHE_NAME = 'crypto-analyzer-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        data: data.data,
        actions: data.actions,
        requireInteraction: data.requireInteraction,
        silent: data.silent
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
});
'''


# 全局实例
push_manager = MobilePushManager()
pwa_config = PWAConfig()

# 便捷函数
def get_push_manager() -> MobilePushManager:
    """获取推送管理器"""
    return push_manager

def register_device(subscription: Dict, user_id: str = None) -> str:
    """注册设备"""
    return push_manager.register_subscription(subscription, user_id)

def send_notification(title: str, body: str, **kwargs):
    """发送通知"""
    return push_manager.send_push(title, body, **kwargs)
