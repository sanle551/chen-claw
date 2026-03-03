#!/usr/bin/env python3
"""
OKX K线分析脚本
获取交易所K线数据，进行技术分析
"""

import requests
import json
import os
from datetime import datetime, timedelta

PROXY = 'http://127.0.0.1:7890'

def get_kline(inst_id, bar='1H', limit=100):
    """获取K线数据"""
    try:
        url = f'https://www.okx.com/api/v5/market/candles?instId={inst_id}&bar={bar}&limit={limit}'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=15)
        data = resp.json()
        
        if data.get('code') == '0':
            # OKX K线格式: [ts, o, h, l, c, vol, volCcy]
            candles = []
            for item in data['data']:
                candles.append({
                    'timestamp': int(item[0]),
                    'open': float(item[1]),
                    'high': float(item[2]),
                    'low': float(item[3]),
                    'close': float(item[4]),
                    'volume': float(item[5]),
                })
            return candles
    except Exception as e:
        print(f"获取K线失败: {e}")
    return None

def calculate_ma(candles, period):
    """计算移动平均线"""
    if len(candles) < period:
        return None
    closes = [c['close'] for c in candles[-period:]]
    return sum(closes) / period

def calculate_rsi(candles, period=14):
    """计算RSI"""
    if len(candles) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, period + 1):
        change = candles[-i]['close'] - candles[-i-1]['close']
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_pattern(candles):
    """检测K线形态"""
    if len(candles) < 3:
        return None
    
    patterns = []
    
    # 最新三根K线
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    
    # 检测锤子线
    body1 = abs(c1['close'] - c1['open'])
    lower_shadow1 = min(c1['close'], c1['open']) - c1['low']
    if lower_shadow1 > body1 * 2 and c1['close'] > c1['open']:
        patterns.append("锤子线(看涨)")
    
    # 检测吞没形态
    body2 = abs(c2['close'] - c2['open'])
    body3 = abs(c3['close'] - c3['open'])
    if c2['close'] < c2['open'] and c3['close'] > c3['open']:
        if c3['open'] < c2['close'] and c3['close'] > c2['open']:
            patterns.append("看涨吞没")
    
    # 检测突破
    if len(candles) >= 20:
        recent_high = max(c['high'] for c in candles[-20:-1])
        if c3['close'] > recent_high:
            patterns.append(f"突破前高 ${recent_high:,.2f}")
    
    return patterns if patterns else None

def analyze_kline(inst_id, bar='1H'):
    """分析K线"""
    print("=" * 70)
    print(f"           OKX K线技术分析 {inst_id} ({bar})")
    print("=" * 70)
    
    candles = get_kline(inst_id, bar)
    if not candles:
        print("获取K线数据失败")
        return
    
    latest = candles[-1]
    
    print(f"\n最新价格: ${latest['close']:,.2f}")
    print(f"24h最高: ${max(c['high'] for c in candles[-24:]):,.2f}")
    print(f"24h最低: ${min(c['low'] for c in candles[-24:]):,.2f}")
    print(f"24h成交量: {sum(c['volume'] for c in candles[-24:]):,.2f}")
    
    # 移动平均线
    print("\n【移动平均线】")
    ma7 = calculate_ma(candles, 7)
    ma20 = calculate_ma(candles, 20)
    ma50 = calculate_ma(candles, 50)
    
    if ma7:
        print(f"MA7:  ${ma7:,.2f} {'> 价格在均线上方' if latest['close'] > ma7 else '< 价格在均线下方'}")
    if ma20:
        print(f"MA20: ${ma20:,.2f} {'> 价格在均线上方' if latest['close'] > ma20 else '< 价格在均线下方'}")
    if ma50:
        print(f"MA50: ${ma50:,.2f} {'> 价格在均线上方' if latest['close'] > ma50 else '< 价格在均线下方'}")
    
    # 均线排列
    if ma7 and ma20 and ma50:
        if ma7 > ma20 > ma50:
            print("✅ 多头排列 (MA7 > MA20 > MA50)")
        elif ma7 < ma20 < ma50:
            print("❌ 空头排列 (MA7 < MA20 < MA50)")
        else:
            print("⚡ 均线纠缠")
    
    # RSI
    rsi = calculate_rsi(candles)
    if rsi:
        print(f"\n【RSI(14)】")
        print(f"RSI: {rsi:.2f}")
        if rsi > 70:
            print("⚠️ 超买区域")
        elif rsi < 30:
            print("⚠️ 超卖区域")
        else:
            print("✅ 中性区域")
    
    # 形态检测
    patterns = detect_pattern(candles)
    if patterns:
        print(f"\n【形态检测】")
        for p in patterns:
            print(f"📊 {p}")
    
    # 支撑压力
    if len(candles) >= 20:
        recent = candles[-20:]
        support = min(c['low'] for c in recent)
        resistance = max(c['high'] for c in recent)
        print(f"\n【支撑压力】")
        print(f"支撑位: ${support:,.2f}")
        print(f"压力位: ${resistance:,.2f}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OKX K线分析')
    parser.add_argument('--symbol', type=str, default='BTC-USDT',
                        help='交易对，如 BTC-USDT')
    parser.add_argument('--bar', type=str, default='1H',
                        help='K线周期: 1m, 5m, 15m, 30m, 1H, 4H, 1D')
    
    args = parser.parse_args()
    
    analyze_kline(args.symbol, args.bar)
