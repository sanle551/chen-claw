#!/usr/bin/env python3
"""
全市场资产全景分析
整合美股、A股、Crypto的持仓分析
"""

import requests
import json
import os
from datetime import datetime

# 配置
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'demo')
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
OKX_API_KEY = os.getenv('OKX_API_KEY', '')
PROXY = 'http://127.0.0.1:7890'

# 汇率（简化处理，实际应该实时获取）
USD_TO_CNY = 7.2

def get_us_stock_price(symbol):
    """获取美股价格"""
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=10)
        data = resp.json()
        return {
            'price': data.get('c', 0),
            'currency': 'USD',
        }
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return None

def get_a_share_price(symbol):
    """获取A股价格"""
    try:
        # 使用东方财富接口
        if symbol.startswith('6'):
            code = f"SH{symbol}"
        else:
            code = f"SZ{symbol}"
        
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={code}&fields=f43,f44,f45,f46,f47,f48,f57,f58'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=10)
        data = resp.json()
        
        if data.get('data'):
            d = data['data']
            price = d.get('f43', 0) / 100 if d.get('f43') else 0
            return {
                'price': price,
                'currency': 'CNY',
                'name': d.get('f58', ''),
            }
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
    return None

def get_crypto_price(symbol):
    """获取Crypto价格"""
    try:
        inst_id = f"{symbol}-USDT"
        url = f'https://www.okx.com/api/v5/market/ticker?instId={inst_id}'
        proxies = {'http': PROXY, 'https': PROXY}
        resp = requests.get(url, proxies=proxies, timeout=10)
        data = resp.json()
        
        if data.get('code') == '0':
            price = float(data['data'][0]['last'])
            return {
                'price': price,
                'currency': 'USD',
            }
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
    return None

def get_crypto_balance(address, chain='BTC'):
    """获取链上余额（简化版，实际需要调用OKX MCP）"""
    # 这里简化处理，实际应该调用 MCP Server
    return None

def analyze_portfolio(holdings_str):
    """
    分析投资组合
    holdings格式: "NVDA:10,AAPL:20,BTC:0.5,600519:100"
    """
    holdings = {}
    for item in holdings_str.split(','):
        if ':' in item:
            symbol, amount = item.split(':')
            holdings[symbol.strip()] = float(amount.strip())
    
    print("=" * 70)
    print(f"              跨市场资产全景分析 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    total_usd = 0
    total_cny = 0
    market_values = {
        'US': {'value': 0, 'items': []},
        'CN': {'value': 0, 'items': []},
        'Crypto': {'value': 0, 'items': []},
    }
    
    for symbol, amount in holdings.items():
        # 判断市场
        if symbol.isdigit():
            # A股
            data = get_a_share_price(symbol)
            if data:
                value_cny = data['price'] * amount
                value_usd = value_cny / USD_TO_CNY
                market_values['CN']['value'] += value_usd
                market_values['CN']['items'].append({
                    'symbol': symbol,
                    'name': data['name'],
                    'amount': amount,
                    'price': data['price'],
                    'value_cny': value_cny,
                    'value_usd': value_usd,
                })
                total_cny += value_cny
                total_usd += value_usd
                print(f"{symbol} ({data['name']}): {amount}股 × ¥{data['price']:.2f} = ¥{value_cny:,.2f}")
        
        elif symbol in ['BTC', 'ETH', 'SOL', 'DOGE']:
            # Crypto
            data = get_crypto_price(symbol)
            if data:
                value_usd = data['price'] * amount
                market_values['Crypto']['value'] += value_usd
                market_values['Crypto']['items'].append({
                    'symbol': symbol,
                    'amount': amount,
                    'price': data['price'],
                    'value_usd': value_usd,
                })
                total_usd += value_usd
                print(f"{symbol}: {amount} × ${data['price']:,.2f} = ${value_usd:,.2f}")
        
        else:
            # 美股
            data = get_us_stock_price(symbol)
            if data:
                value_usd = data['price'] * amount
                market_values['US']['value'] += value_usd
                market_values['US']['items'].append({
                    'symbol': symbol,
                    'amount': amount,
                    'price': data['price'],
                    'value_usd': value_usd,
                })
                total_usd += value_usd
                print(f"{symbol}: {amount}股 × ${data['price']:.2f} = ${value_usd:,.2f}")
    
    # 输出汇总
    print("\n" + "-" * 70)
    print("资产分布:")
    print("-" * 70)
    
    for market, data in market_values.items():
        if data['value'] > 0:
            pct = (data['value'] / total_usd * 100) if total_usd > 0 else 0
            market_name = {'US': '美股', 'CN': 'A股', 'Crypto': 'Crypto'}[market]
            print(f"{market_name}: ${data['value']:,.2f} ({pct:.1f}%)")
    
    print("-" * 70)
    print(f"总资产: ${total_usd:,.2f} (≈ ¥{total_usd * USD_TO_CNY:,.2f})")
    print("=" * 70)
    
    # 风险分析
    print("\n风险分析:")
    crypto_pct = (market_values['Crypto']['value'] / total_usd * 100) if total_usd > 0 else 0
    if crypto_pct > 30:
        print(f"⚠️ Crypto占比 {crypto_pct:.1f}%，风险较高")
    elif crypto_pct > 10:
        print(f"⚡ Crypto占比 {crypto_pct:.1f}%，中等风险")
    else:
        print(f"✅ Crypto占比 {crypto_pct:.1f}%，风险可控")
    
    return {
        'total_usd': total_usd,
        'total_cny': total_usd * USD_TO_CNY,
        'market_values': market_values,
    }

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='全市场资产全景分析')
    parser.add_argument('--holdings', type=str, required=True,
                        help='持仓，格式: "NVDA:10,AAPL:20,BTC:0.5,600519:100"')
    
    args = parser.parse_args()
    
    analyze_portfolio(args.holdings)
