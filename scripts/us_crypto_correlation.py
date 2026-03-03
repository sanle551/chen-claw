#!/usr/bin/env python3
"""
美股-Crypto 联动监控脚本
监控 MSTR、COIN、HOOD、NVDA 等美股与 BTC、ETH 等 Crypto 的关联
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import statistics

# 配置
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'demo')
OKX_API_KEY = os.getenv('OKX_API_KEY', '')
PROXY = 'http://127.0.0.1:7890'

# 美股-Crypto 映射
US_CRYPTO_MAP = {
    'MSTR': {'crypto': 'BTC', 'name': 'MicroStrategy', 'logic': '持有大量BTC'},
    'COIN': {'crypto': 'BTC,ETH', 'name': 'Coinbase', 'logic': '交易所收入与交易量相关'},
    'HOOD': {'crypto': 'DOGE,BTC', 'name': 'Robinhood', 'logic': '散户交易量大'},
    'NVDA': {'crypto': 'TAO,FET', 'name': 'NVIDIA', 'logic': 'AI算力叙事'},
}

def get_us_stock_price(symbol):
    """获取美股价格"""
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=10)
        data = resp.json()
        return {
            'price': data.get('c', 0),
            'open': data.get('o', 0),
            'high': data.get('h', 0),
            'low': data.get('l', 0),
            'prev_close': data.get('pc', 0),
        }
    except Exception as e:
        print(f"获取 {symbol} 股价失败: {e}")
        return None

def get_okx_price(inst_id):
    """获取 OKX 交易所价格"""
    try:
        url = f'https://www.okx.com/api/v5/market/ticker?instId={inst_id}'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=10)
        data = resp.json()
        if data.get('code') == '0':
            d = data['data'][0]
            return {
                'price': float(d['last']),
                'open': float(d['open24h']),
                'high': float(d['high24h']),
                'low': float(d['low24h']),
                'change_24h': ((float(d['last']) - float(d['open24h'])) / float(d['open24h']) * 100) if float(d['open24h']) > 0 else 0,
            }
    except Exception as e:
        print(f"获取 {inst_id} 价格失败: {e}")
    return None

def calculate_correlation(stock_changes, crypto_changes):
    """计算相关系数"""
    if len(stock_changes) != len(crypto_changes) or len(stock_changes) < 2:
        return 0
    
    n = len(stock_changes)
    mean_stock = sum(stock_changes) / n
    mean_crypto = sum(crypto_changes) / n
    
    numerator = sum((s - mean_stock) * (c - mean_crypto) for s, c in zip(stock_changes, crypto_changes))
    denom_stock = sum((s - mean_stock) ** 2 for s in stock_changes) ** 0.5
    denom_crypto = sum((c - mean_crypto) ** 2 for c in crypto_changes) ** 0.5
    
    if denom_stock == 0 or denom_crypto == 0:
        return 0
    
    return numerator / (denom_stock * denom_crypto)

def detect_divergence(stock_data, crypto_data):
    """检测背离信号"""
    if not stock_data or not crypto_data:
        return None
    
    stock_change = ((stock_data['price'] - stock_data['prev_close']) / stock_data['prev_close'] * 100) if stock_data['prev_close'] > 0 else 0
    crypto_change = crypto_data['change_24h']
    
    diff = abs(stock_change - crypto_change)
    
    if diff > 5:  # 差异超过5%
        if stock_change > crypto_change:
            return f"股价高估 {diff:.1f}% (股价+{stock_change:.1f}% vs 币价+{crypto_change:.1f}%)"
        else:
            return f"股价低估 {diff:.1f}% (股价+{stock_change:.1f}% vs 币价+{crypto_change:.1f}%)"
    
    return None

def get_correlation_level(corr):
    """获取相关程度描述"""
    abs_corr = abs(corr)
    if abs_corr >= 0.8:
        return "强相关"
    elif abs_corr >= 0.5:
        return "中等相关"
    elif abs_corr >= 0.3:
        return "弱相关"
    else:
        return "无相关"

def monitor_us_crypto(stocks=None, cryptos=None):
    """监控美股-Crypto联动"""
    if stocks is None:
        stocks = list(US_CRYPTO_MAP.keys())
    
    print("=" * 70)
    print(f"           美股-Crypto 联动监控报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    results = []
    
    for stock in stocks:
        if stock not in US_CRYPTO_MAP:
            continue
        
        info = US_CRYPTO_MAP[stock]
        crypto_list = info['crypto'].split(',')
        
        print(f"\n【{stock} - {info['name']}】")
        print(f"逻辑: {info['logic']}")
        
        # 获取股价
        stock_data = get_us_stock_price(stock)
        if stock_data:
            stock_change = ((stock_data['price'] - stock_data['prev_close']) / stock_data['prev_close'] * 100) if stock_data['prev_close'] > 0 else 0
            print(f"股价: ${stock_data['price']:.2f} ({stock_change:+.2f}%)")
        else:
            print("股价: 获取失败")
            continue
        
        # 获取关联币价
        for crypto in crypto_list:
            inst_id = f"{crypto}-USDT"
            crypto_data = get_okx_price(inst_id)
            
            if crypto_data:
                print(f"{crypto}: ${crypto_data['price']:,.2f} ({crypto_data['change_24h']:+.2f}%)")
                
                # 检测背离
                divergence = detect_divergence(stock_data, crypto_data)
                if divergence:
                    print(f"⚠️ 背离信号: {divergence}")
                else:
                    print(f"✅ 联动正常")
            else:
                print(f"{crypto}: 获取失败")
        
        results.append({
            'stock': stock,
            'stock_data': stock_data,
            'info': info,
        })
    
    print("\n" + "=" * 70)
    print("提示: 背离信号仅供参考，不构成投资建议")
    print("=" * 70)
    
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='美股-Crypto联动监控')
    parser.add_argument('--stocks', type=str, default='MSTR,COIN,HOOD,NVDA',
                        help='监控的美股，逗号分隔')
    parser.add_argument('--cryptos', type=str, default='BTC,ETH,DOGE',
                        help='监控的Crypto，逗号分隔')
    
    args = parser.parse_args()
    
    stocks = args.stocks.split(',')
    monitor_us_crypto(stocks)
