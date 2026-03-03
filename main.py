#!/usr/bin/env python3
"""
加密货币每日智能分析系统主入口
"""
import json
import sys
from datetime import datetime
from src.data_fetcher import DataFetcher
from src.analyzer import CryptoAnalyzer
from src.notifier import TelegramNotifier
from src.llm_client import GeminiClient
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def load_tokens():
    """加载监控代币配置"""
    with open('config/tokens.json', 'r') as f:
        config = json.load(f)
    return config.get('tokens', [])

def main():
    print("=" * 60)
    print("🚀 Crypto Daily Analyzer 启动")
    print("=" * 60)
    
    # 初始化组件
    data_fetcher = DataFetcher()
    llm_client = GeminiClient()
    analyzer = CryptoAnalyzer(llm_client)
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # 加载代币配置
    tokens = load_tokens()
    print(f"📊 加载了 {len(tokens)} 个监控代币")
    
    # 获取市场概览
    print("\n📈 获取市场概览...")
    market_overview = data_fetcher.get_market_overview()
    
    # 分析每个代币
    analyses = []
    print("\n🔍 开始分析代币...")
    for i, token in enumerate(tokens, 1):
        symbol = token['symbol']
        print(f"\n[{i}/{len(tokens)}] 分析 {symbol}...")
        
        try:
            # 获取数据
            price_data = data_fetcher.get_price_data(token)
            news_data = data_fetcher.get_news_data(symbol)
            
            # 分析
            analysis = analyzer.analyze_token(token, price_data, news_data)
            analyses.append(analysis)
            
            print(f"✅ {symbol} 分析完成 - 评级: {analysis['rating']}")
        except Exception as e:
            print(f"❌ {symbol} 分析失败: {e}")
            continue
    
    # 生成报告
    print("\n📝 生成分析报告...")
    report = analyzer.generate_daily_report(market_overview, analyses)
    
    # 推送报告
    print("\n📤 推送报告到 Telegram...")
    notifier.send_report(report)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
