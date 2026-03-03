"""
🔄 实时价格监控技能
WebSocket实时价格流 + 变动检测 + 智能预警
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
import threading
import logging

try:
    import websockets
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

LOGGER = logging.getLogger("price_monitor")

class PriceMonitor:
    """实时价格监控器"""
    
    def __init__(self):
        self.price_cache: Dict[str, dict] = {}
        self.subscribers: List[Callable] = []
        self.alert_rules: List[dict] = []
        self.running = False
        self.ws_connections: Dict[str, object] = {}
        self._lock = threading.Lock()
        
    def subscribe(self, callback: Callable):
        """订阅价格更新"""
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            
    def add_alert_rule(self, symbol: str, threshold_pct: float, 
                       direction: str = "both", callback: Optional[Callable] = None):
        """添加预警规则
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            threshold_pct: 变动阈值百分比
            direction: 方向 - "up"(涨)/"down"(跌)/"both"(双向)
            callback: 触发时的回调函数
        """
        rule = {
            "id": f"{symbol}_{int(time.time())}",
            "symbol": symbol,
            "threshold_pct": threshold_pct,
            "direction": direction,
            "callback": callback,
            "last_price": None,
            "last_triggered": None
        }
        self.alert_rules.append(rule)
        LOGGER.info(f"添加预警规则: {symbol} {direction} {threshold_pct}%")
        
    def remove_alert_rule(self, rule_id: str):
        """删除预警规则"""
        self.alert_rules = [r for r in self.alert_rules if r["id"] != rule_id]
        
    def update_price(self, symbol: str, price: float, source: str = "unknown"):
        """更新价格"""
        with self._lock:
            old_data = self.price_cache.get(symbol)
            
            new_data = {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "source": source
            }
            
            if old_data:
                old_price = old_data["price"]
                change_pct = ((price - old_price) / old_price) * 100
                new_data["change_24h"] = change_pct
                new_data["change_amount"] = price - old_price
                
                # 检查预警
                self._check_alerts(symbol, price, change_pct)
            
            self.price_cache[symbol] = new_data
            
        # 通知订阅者
        for subscriber in self.subscribers:
            try:
                subscriber(new_data)
            except Exception as e:
                LOGGER.error(f"订阅者回调错误: {e}")
                
    def _check_alerts(self, symbol: str, price: float, change_pct: float):
        """检查是否触发预警"""
        for rule in self.alert_rules:
            if rule["symbol"] != symbol:
                continue
                
            # 检查触发条件
            triggered = False
            direction = rule["direction"]
            threshold = rule["threshold_pct"]
            
            if direction == "up" and change_pct >= threshold:
                triggered = True
            elif direction == "down" and change_pct <= -threshold:
                triggered = True
            elif direction == "both" and abs(change_pct) >= threshold:
                triggered = True
                
            if triggered:
                # 防抖：同一规则30秒内不重复触发
                last_triggered = rule.get("last_triggered")
                if last_triggered and (time.time() - last_triggered) < 30:
                    continue
                    
                rule["last_triggered"] = time.time()
                rule["last_price"] = price
                
                alert_data = {
                    "rule_id": rule["id"],
                    "symbol": symbol,
                    "price": price,
                    "change_pct": change_pct,
                    "direction": "up" if change_pct > 0 else "down",
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat()
                }
                
                LOGGER.warning(f"🚨 价格预警触发: {symbol} {change_pct:+.2f}%")
                
                # 执行回调
                if rule["callback"]:
                    try:
                        rule["callback"](alert_data)
                    except Exception as e:
                        LOGGER.error(f"预警回调错误: {e}")
                        
    def get_price(self, symbol: str) -> Optional[dict]:
        """获取当前价格"""
        return self.price_cache.get(symbol)
        
    def get_all_prices(self) -> Dict[str, dict]:
        """获取所有价格"""
        return self.price_cache.copy()
        
    def start_monitoring(self, symbols: List[str], interval: int = 5):
        """开始监控（轮询模式）"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    for symbol in symbols:
                        # 这里应该调用实际的API获取价格
                        # 示例：模拟价格更新
                        pass
                    time.sleep(interval)
                except Exception as e:
                    LOGGER.error(f"监控循环错误: {e}")
                    time.sleep(1)
                    
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        LOGGER.info(f"开始价格监控: {symbols}, 间隔: {interval}s")
        
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        LOGGER.info("停止价格监控")


class WebSocketPriceFeed:
    """WebSocket实时价格流"""
    
    EXCHANGE_WS_URLS = {
        "binance": "wss://stream.binance.com:9443/ws/{symbol}@ticker",
        "coinbase": "wss://ws-feed.exchange.coinbase.com",
        "kraken": "wss://ws.kraken.com"
    }
    
    def __init__(self, monitor: PriceMonitor):
        self.monitor = monitor
        self.connections = {}
        self.running = False
        
    async def connect_binance(self, symbols: List[str]):
        """连接 Binance WebSocket"""
        if not WEBSOCKET_AVAILABLE:
            LOGGER.error("websockets库未安装")
            return
            
        streams = "/".join([f"{s.lower()}@ticker" for s in symbols])
        url = f"wss://stream.binance.com:9443/ws/{streams}"
        
        try:
            async with websockets.connect(url) as ws:
                self.connections["binance"] = ws
                LOGGER.info(f"连接 Binance WebSocket: {symbols}")
                
                async for message in ws:
                    if not self.running:
                        break
                    try:
                        data = json.loads(message)
                        symbol = data.get("s", "").upper()
                        price = float(data.get("c", 0))
                        change_pct = float(data.get("P", 0))
                        
                        self.monitor.update_price(symbol, price, "binance_ws")
                    except Exception as e:
                        LOGGER.error(f"处理消息错误: {e}")
                        
        except Exception as e:
            LOGGER.error(f"WebSocket连接错误: {e}")
            
    def start(self, exchange: str = "binance", symbols: List[str] = None):
        """启动WebSocket连接"""
        if not symbols:
            symbols = ["BTCUSDT", "ETHUSDT"]
            
        self.running = True
        
        if exchange == "binance":
            asyncio.create_task(self.connect_binance(symbols))
            
    def stop(self):
        """停止WebSocket"""
        self.running = False
        for conn in self.connections.values():
            try:
                asyncio.create_task(conn.close())
            except:
                pass


# 全局实例
price_monitor = PriceMonitor()
ws_feed = WebSocketPriceFeed(price_monitor)

# 便捷函数
def get_monitor() -> PriceMonitor:
    """获取价格监控器实例"""
    return price_monitor

def add_price_alert(symbol: str, threshold: float, callback: Callable = None):
    """添加价格预警"""
    price_monitor.add_alert_rule(symbol, threshold, callback=callback)
    
def get_current_price(symbol: str) -> Optional[float]:
    """获取当前价格"""
    data = price_monitor.get_price(symbol)
    return data["price"] if data else None
