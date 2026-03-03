#!/usr/bin/env python3
"""
综合跨市场监控脚本
整合所有功能，提供统一的监控面板
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from us_crypto_correlation import monitor_us_crypto
from portfolio_analyzer import analyze_portfolio
from okx_kline_analysis import analyze_kline

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 70)
    print("              全市场联动监控系统")
    print("=" * 70)
    print("\n1. 美股-Crypto 联动监控")
    print("2. 全市场资产全景分析")
    print("3. OKX K线技术分析")
    print("4. 综合报告")
    print("5. 退出")
    print("\n" + "=" * 70)

def run_interactive():
    """交互式运行"""
    while True:
        show_menu()
        choice = input("\n请选择功能 (1-5): ").strip()
        
        if choice == '1':
            stocks = input("输入美股代码 (默认 MSTR,COIN,HOOD,NVDA): ").strip()
            if not stocks:
                stocks = "MSTR,COIN,HOOD,NVDA"
            monitor_us_crypto(stocks.split(','))
        
        elif choice == '2':
            holdings = input("输入持仓 (格式: NVDA:10,BTC:0.5,600519:100): ").strip()
            if holdings:
                analyze_portfolio(holdings)
        
        elif choice == '3':
            symbol = input("输入交易对 (默认 BTC-USDT): ").strip()
            if not symbol:
                symbol = "BTC-USDT"
            bar = input("K线周期 (默认 1H): ").strip()
            if not bar:
                bar = "1H"
            analyze_kline(symbol, bar)
        
        elif choice == '4':
            print("\n生成综合报告...")
            print("\n【美股-Crypto联动】")
            monitor_us_crypto(['MSTR', 'COIN'])
            print("\n【BTC技术分析】")
            analyze_kline('BTC-USDT', '1H')
        
        elif choice == '5':
            print("\n再见!")
            break
        
        else:
            print("\n无效选择，请重试")
        
        input("\n按回车继续...")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='全市场联动监控系统')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='交互式模式')
    parser.add_argument('--report', '-r', action='store_true',
                        help='生成综合报告')
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    elif args.report:
        print("\n【美股-Crypto联动】")
        monitor_us_crypto(['MSTR', 'COIN'])
        print("\n【BTC技术分析】")
        analyze_kline('BTC-USDT', '1H')
    else:
        run_interactive()
