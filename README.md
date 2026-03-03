# Cross-Market Intelligence

全市场联动监控系统 - 整合美股、A股、Crypto交易所和链上数据的跨市场分析工具。

## 功能特性

- 美股-Crypto 联动监控
- 全市场资产全景分析
- OKX K线技术分析
- 综合监控面板

## 安装

```bash
pip install requests pandas numpy
```

## 环境变量

```bash
export FINNHUB_API_KEY="your-finnhub-key"
export TUSHARE_TOKEN="your-tushare-token"
export OKX_API_KEY="your-okx-api-key"
```

## 使用方法

```bash
# 交互式模式
python scripts/cross_market_monitor.py -i

# 生成报告
python scripts/cross_market_monitor.py -r

# 单独功能
python scripts/us_crypto_correlation.py --stocks MSTR,COIN
python scripts/portfolio_analyzer.py --holdings "NVDA:10,BTC:0.5"
python scripts/okx_kline_analysis.py --symbol BTC-USDT --bar 1H
```

## 作者

- GitHub: [@sanle551](https://github.com/sanle551)
