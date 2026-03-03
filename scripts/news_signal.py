#!/usr/bin/env python3
"""
新闻驱动交易信号分析
使用 OpenNews 6551 API 获取加密新闻并生成交易信号
"""

import requests
import json
import os
from datetime import datetime

OPENNEWS_TOKEN = os.getenv('OPENNEWS_TOKEN', '')

def search_news(keywords=None, coins=None, limit=10):
    """搜索新闻"""
    try:
        url = "https://ai.6551.io/open/news_search"
        headers = {
            "Authorization": f"Bearer {OPENNEWS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {"limit": limit, "page": 1}
        if keywords:
            payload["q"] = keywords
        if coins:
            payload["coins"] = coins
        
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return None

def analyze_news_signal(news_data):
    """分析新闻信号"""
    if not news_data or not news_data.get('success'):
        return None
    
    articles = news_data.get('data', [])
    signals = []
    
    for item in articles:
        ai_rating = item.get('aiRating')
        if ai_rating and ai_rating.get('status') == 'done':
            signals.append({
                'text': item['text'][:80] + '...' if len(item['text']) > 80 else item['text'],
                'score': ai_rating.get('score', 0),
                'grade': ai_rating.get('grade', 'C'),
                'signal': ai_rating.get('signal', 'neutral'),
                'source': item.get('newsType', 'Unknown'),
                'time': item.get('ts', '')[:10],
            })
    
    return signals

def generate_trading_signals(signals):
    """生成交易信号"""
    if not signals:
        return "暂无有效信号"
    
    # 按评分排序
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    bullish = [s for s in signals if s['signal'] == 'long']
    bearish = [s for s in signals if s['signal'] == 'short']
    neutral = [s for s in signals if s['signal'] == 'neutral']
    
    result = []
    
    if bullish:
        result.append(f"\n📈 看涨信号 ({len(bullish)}条):")
        for s in bullish[:3]:
            result.append(f"  • [{s['grade']}] {s['text']} (评分: {s['score']})")
    
    if bearish:
        result.append(f"\n📉 看跌信号 ({len(bearish)}条):")
        for s in bearish[:3]:
            result.append(f"  • [{s['grade']}] {s['text']} (评分: {s['score']})")
    
    if neutral:
        result.append(f"\n⚖️ 中性信号 ({len(neutral)}条):")
        for s in neutral[:3]:
            result.append(f"  • [{s['grade']}] {s['text']} (评分: {s['score']})")
    
    return '\n'.join(result)

def main():
    """主函数"""
    print("=" * 70)
    print(f"           新闻驱动交易信号分析 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # 搜索 BTC 相关新闻
    print("\n【搜索 BTC 相关新闻】")
    news_data = search_news(coins=["BTC"], limit=20)
    
    if news_data:
        signals = analyze_news_signal(news_data)
        if signals:
            print(generate_trading_signals(signals))
        else:
            print("暂无 AI 评分完成的新闻")
    
    # 搜索关键词
    print("\n" + "-" * 70)
    print("\n【搜索 'Bitcoin ETF' 相关新闻】")
    news_data = search_news(keywords="Bitcoin ETF", limit=10)
    
    if news_data:
        signals = analyze_news_signal(news_data)
        if signals:
            print(generate_trading_signals(signals))
        else:
            print("暂无 AI 评分完成的新闻")
    
    print("\n" + "=" * 70)
    print("提示: 新闻信号仅供参考，不构成投资建议")
    print("=" * 70)

if __name__ == '__main__':
    main()
