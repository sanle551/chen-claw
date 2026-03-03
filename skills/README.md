# 📊 Crypto Daily Analyzer - Skills Hub
# 加密货币技能整合中心

## 🎯 已整合技能

### 1. 核心分析技能
- **crypto-price**: 实时加密货币价格查询
- **market-news**: 市场新闻聚合
- **trading-signals**: 交易信号生成
- **crypto-deep-analysis**: 12模块深度分析框架

### 2. 新增技能
- **🔄 real-time-monitor**: 实时价格监控与预警
- **📱 mobile-push**: 移动端推送 (PWA + Push API)
- **🤖 ai-analysis-hub**: AI多模型分析整合

### 3. 数据源技能
- **6551-opennews**: 新闻 + AI评级
- **6551-opentwitter**: 社交舆情
- **coingecko-api**: 市场数据
- **defillama**: DeFi数据

## 📁 技能目录结构

```
skills/
├── core/                   # 核心技能
│   ├── price_monitor/     # 实时价格监控 🔄
│   ├── mobile_push/       # 移动端推送 📱
│   └── ai_hub/            # AI分析整合 🤖
├── data/                  # 数据源技能
│   ├── coingecko/
│   ├── defillama/
│   ├── opennews/
│   └── opentwitter/
├── analysis/              # 分析技能
│   ├── deep_analyzer/
│   ├── signal_generator/
│   └── strategy_backtest/
└── utils/                 # 工具技能
    ├── telegram_bot/
    ├── chart_renderer/
    └── alert_manager/
```

## 🚀 快速开始

```bash
# 启用技能
python skills/enable.py price_monitor
python skills/enable.py mobile_push
python skills/enable.py ai_hub

# 查看技能状态
python skills/status.py
```

## 📚 技能文档

每个技能目录包含：
- `SKILL.md` - 技能说明文档
- `config.json` - 配置文件
- `__init__.py` - 入口
- `README.md` - 使用指南
