# Chen-Claw Skills Collection

个人定制的 OpenClaw 技能集合，涵盖美股、A股、加密货币分析。

## 📁 技能目录

### 🇺🇸 美股分析

| 技能 | 路径 | 描述 |
|------|------|------|
| **tech-earnings-deepdive** | [`_skills/tech-earnings-deepdive/`](./_skills/tech-earnings-deepdive/) | 美股财报深度分析（16模块+6视角框架） |
| **finnhub** | [`_skills/finnhub/`](./_skills/finnhub/) | Finnhub API 股票数据 |

### 💰 加密货币分析

| 技能 | 路径 | 描述 |
|------|------|------|
| **crypto-token-deepdive** | [`_skills/crypto-token-deepdive/`](./_skills/crypto-token-deepdive/) | 加密货币代币深度分析框架 |
| **bitget-wallet-skill** | [`_skills/bitget-wallet-skill/`](./_skills/bitget-wallet-skill/) | Bitget钱包链上数据+swap |
| **opennews** | [`_skills/opennews/`](./_skills/opennews/) | 6551加密新闻 |
| **opentwitter** | [`_skills/opentwitter/`](./_skills/opentwitter/) | 6551 Twitter数据 |

### 🇨🇳 A股分析

| 技能 | 路径 | 描述 |
|------|------|------|
| **a-share-deepdive** | [`_skills/a-share-deepdive/`](./_skills/a-share-deepdive/) | A股财报深度分析框架（16模块+6视角） |
| **sector** | [`_skills/sector/`](./_skills/sector/) | A股板块分析（东方财富爬虫） |
| **a-share-tushare** | [`_skills/a-share-tushare/`](./_skills/a-share-tushare/) | Tushare Pro数据接口 |
| **a-share-em** | [`_skills/a-share-em/`](./_skills/a-share-em/) | 东方财富API（无依赖） |
| **a-share-finance** | [`_skills/a-share-finance/`](./_skills/a-share-finance/) | A股财务数据补充 |
| **eastmoney-api** | [`_skills/eastmoney-api/`](./_skills/eastmoney-api/) | 东方财富接口文档 |

### 📊 通用工具

| 技能 | 路径 | 描述 |
|------|------|------|
| **crypto-price** | [`crypto-price.js`](./crypto-price.js) | 加密货币价格查询 |
| **market-news** | [`market-news.js`](./market-news.js) | 市场新闻 |
| **stock-screener** | [`stock-screener.js`](./stock-screener.js) | 股票筛选器 |
| **trading-signals** | [`trading-signals.js`](./trading-signals.js) | 交易信号 |

## 🚀 快速开始

### 安装所有技能

```bash
# 克隆到 OpenClaw skills 目录
git clone https://github.com/sanle551/chen-claw.git ~/.openclaw/workspace/skills
```

### 安装单个技能

```bash
# 例如安装 A股深度分析
cp -r _skills/a-share-deepdive ~/.openclaw/workspace/skills/
```

## 📋 依赖安装

```bash
# Python 依赖
pip install akshare tushare

# Node.js 依赖（部分技能需要）
npm install
```

## 🔑 API Token 配置

| 数据源 | Token 获取 | 环境变量 |
|--------|-----------|---------|
| Tushare | https://tushare.pro/register | `TUSHARE_TOKEN` |
| 6551 | https://6551.io/mcp | `OPENNEWS_TOKEN`, `TWITTER_TOKEN` |
| Bitget | https://www.bitget.com | `BGW_API_KEY` |

## 📖 使用示例

### 美股分析
```bash
# 分析某只美股
"帮我分析 NVDA 最新财报"
```

### A股分析
```bash
# 分析某只A股
"帮我分析 000001 平安银行"

# 查看板块热度
"当前A股哪些板块最热"
```

### 加密货币分析
```bash
# 分析代币
"分析这个代币: 0x... on Solana"

# 获取新闻
"最新加密新闻"
```

## 🛠️ 技能开发

### 技能结构
```
_skill-name/
├── SKILL.md          # 技能主文件（必需）
├── references/       # 参考文档
│   ├── xxx.md
│   └── yyy.md
├── scripts/          # 脚本文件
│   └── xxx.py
└── assets/           # 静态资源
    └── xxx.png
```

### SKILL.md 格式
```yaml
---
name: skill-name
description: 技能描述
---

# 技能标题

## 功能说明
...

## 使用方法
...
```

## 📚 文档

- [美股财报分析框架](./_skills/tech-earnings-deepdive/SKILL.md)
- [A股深度分析框架](./_skills/a-share-deepdive/SKILL.md)
- [加密货币分析框架](./_skills/crypto-token-deepdive/SKILL.md)
- [东方财富API文档](./_skills/eastmoney-api/SKILL.md)

## 🤝 贡献

欢迎提交 PR 或 Issue。

## 📄 License

MIT License

## 👤 作者

- GitHub: [@sanle551](https://github.com/sanle551)
