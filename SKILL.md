# Cross-Market Intelligence

全市场联动监控系统 - 整合美股、A股、Crypto交易所和链上数据的跨市场分析工具。

## 功能特性

### 1. 美股-Crypto 联动监控
- 监控 MSTR、COIN、HOOD、NVDA 等美股与 Crypto 的关联
- 实时计算相关系数和背离信号
- 生成套利/对冲交易建议

### 2. 全市场资产全景
- 统一计算跨市场持仓价值
- 风险敞口分析
- 相关性矩阵

### 3. 新闻驱动交易信号
- 监控加密新闻和 Twitter KOL
- 情绪分析和关键词提取
- 新闻-价格联动信号

### 4. A股-Crypto 概念联动
- 电力股 vs 算力代币
- 芯片股 vs AI 代币
- 跨市场叙事验证

### 5. OKX 交易所数据整合
- 实时价格和 K 线
- 成交量和深度分析
- 与美股/A股的技术形态对比

## 安装

### 依赖安装
```bash
pip install requests pandas numpy akshare tushare
npm install -g @anthropic-ai/claude-code
```

### MCP Server 配置
```bash
# OKX Web3 Market MCP
claude mcp add onchainos-mcp https://web3.okx.com/api/v1/onchainos-mcp \
  -t http -H "OK-ACCESS-KEY: your-api-key"
```

### 环境变量
```bash
export TUSHARE_TOKEN="your-tushare-token"
export FINNHUB_API_KEY="your-finnhub-key"
export OKX_API_KEY="your-okx-api-key"
export OPENNEWS_TOKEN="your-opennews-token"
export TWITTER_TOKEN="your-twitter-token"
```

## 使用方法

### 命令行使用
```bash
# 监控美股-Crypto联动
python scripts/us_crypto_correlation.py --stocks MSTR,COIN --crypto BTC,ETH

# 全市场资产分析
python scripts/portfolio_analyzer.py --holdings "NVDA:10,AAPL:20,BTC:0.5"

# 新闻驱动信号
python scripts/news_signal.py --keywords "Bitcoin ETF,美联储"

# A股-Crypto概念联动
python scripts/a_share_crypto.py --sector power --crypto RNDR,FIL

# OKX K线分析
python scripts/okx_kline_analysis.py --symbol BTC-USDT --bar 1H
```

### Claude 中使用
```
"监控 MSTR 和 BTC 的联动情况"
"分析我的持仓: NVDA, 茅台, BTC"
"今天有什么加密新闻驱动了价格?"
"电力板块和算力代币的关联如何?"
"BTC 1小时K线突破了吗?"
```

## 数据源

| 市场 | 数据源 | 数据类型 |
|------|--------|----------|
| 美股 | Finnhub | 股价、财报 |
| A股 | Tushare/东方财富 | 股价、板块、财务 |
| Crypto交易所 | OKX API | 现货价格、K线、深度 |
| Crypto链上 | OKX MCP | 余额、DEX价格、持仓 |
| 新闻 | opennews | 加密新闻 |
| 社交 | opentwitter | KOL动态 |

## 输出示例

### 联动监控报告
```
╔══════════════════════════════════════════════════════════════╗
║              美股-Crypto 联动监控报告 2026-03-03 18:00        ║
╠══════════════════════════════════════════════════════════════╣
║ MSTR vs BTC                                                  ║
║   股价: $XXX.XX    币价: $XX,XXX                             ║
║   24h相关系数: 0.87 (强相关)                                  ║
║   背离信号: 无                                               ║
║   建议: 持有                                                 ║
╠══════════════════════════════════════════════════════════════╣
║ COIN vs BTC                                                  ║
║   股价: $XXX.XX    币价: $XX,XXX                             ║
║   24h相关系数: 0.72 (中等相关)                                ║
║   背离信号: 股价低估 3%                                       ║
║   建议: 关注买入机会                                          ║
╚══════════════════════════════════════════════════════════════╝
```

### 资产全景报告
```
╔══════════════════════════════════════════════════════════════╗
║                   跨市场资产全景 2026-03-03                   ║
╠══════════════════════════════════════════════════════════════╣
║ 总资产价值: $XXX,XXX (¥XXX万)                                ║
║                                                              ║
║ 市场分布:                                                    ║
║   美股: 45% ($XXX,XXX)                                       ║
║   A股: 30% ($XXX,XXX)                                        ║
║   Crypto: 25% ($XXX,XXX)                                     ║
║                                                              ║
║ 风险敞口:                                                    ║
║   科技股: 55% (高风险)                                       ║
║   Crypto: 25% (高风险)                                       ║
║   传统资产: 20% (低风险)                                     ║
╚══════════════════════════════════════════════════════════════╝
```

## 项目结构

```
cross-market-intelligence/
├── SKILL.md                    # 技能主文档
├── scripts/
│   ├── us_crypto_correlation.py    # 美股-Crypto联动
│   ├── portfolio_analyzer.py       # 资产全景分析
│   ├── news_signal.py              # 新闻驱动信号
│   ├── a_share_crypto.py           # A股-Crypto联动
│   ├── okx_kline_analysis.py       # OKX K线分析
│   └── cross_market_monitor.py     # 综合监控
├── references/
│   ├── okx_api_reference.md        # OKX API参考
│   └── correlation_study.md        # 联动研究
├── assets/
│   └── example_report.png          # 示例报告
└── README.md
```

## 作者

- GitHub: [@sanle551](https://github.com/sanle551)

## License

MIT License
