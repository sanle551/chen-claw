# 📊 Crypto Daily Analyzer
# 加密货币每日智能分析系统

基于 LLM 的加密货币智能分析系统，每日自动分析自选代币并推送「决策仪表盘」到 Telegram

## ✨ 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| 🤖 AI | 决策仪表盘 | 一句话核心结论 + 精确买卖点位 + 操作检查清单 |
| 📈 分析 | 多维度分析 | 技术面（实时指标）+ 链上数据 + 舆情情报 + 市场情绪 |
| 🌍 市场 | 全链监控 | 支持 ETH、BSC、Base、Solana 等多链代币 |
| 📊 策略 | 市场策略系统 | 内置「趋势跟随策略」与「均值回归策略」，输出进攻/均衡/防守计划 |
| 📰 复盘 | 市场复盘 | 每日市场概览、板块涨跌、资金流向 |
| 🔔 推送 | 多渠道通知 | Telegram、企业微信、飞书、钉钉 |
| ⏰ 自动化 | 定时运行 | GitHub Actions / Cron 定时执行，无需服务器 |

## 🛠️ 技术栈

- **AI 模型**: Gemini 3.1 Pro / OpenAI / Claude (通过 OpenRouter)
- **行情数据**: CoinGecko API、DexScreener API
- **链上数据**: DeFiLlama、Dune Analytics
- **新闻舆情**: 6551 OpenNews、6551 OpenTwitter
- **推送**: Telegram Bot API

## 📁 项目结构

```
crypto-daily-analyzer/
├── config/
│   └── tokens.json          # 监控代币配置
├── src/
│   ├── __init__.py
│   ├── analyzer.py          # 核心分析引擎
│   ├── data_fetcher.py      # 数据获取
│   ├── llm_client.py        # LLM 客户端
│   ├── technical_analysis.py # 技术分析
│   ├── onchain_analysis.py  # 链上分析
│   └── notifier.py          # 推送通知
├── templates/
│   └── report_template.md   # 报告模板
├── .github/
│   └── workflows/
│       └── daily-analysis.yml  # GitHub Actions
├── requirements.txt
├── config.py
├── main.py
└── README.md
```

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）

#### 1. Fork 本仓库

#### 2. 配置 Secrets

Settings → Secrets and variables → Actions → New repository secret

**必需配置：**

| Secret | 说明 | 获取方式 |
|--------|------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 发送消息给 bot 获取 |
| `GEMINI_API_KEY` | Gemini API Key | Google AI Studio |
| `OPENNEWS_TOKEN` | 6551 OpenNews Token | 6551.io |
| `TWITTER_TOKEN` | 6551 OpenTwitter Token | 6551.io |

**可选配置：**
- `OPENROUTER_API_KEY` - OpenRouter API Key（备用模型）
- `COINGECKO_API_KEY` - CoinGecko Pro API Key

#### 3. 配置监控代币

编辑 `config/tokens.json`：

```json
{
  "tokens": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "coingecko_id": "bitcoin",
      "chain": "bitcoin",
      "contract": null,
      "type": "major"
    },
    {
      "symbol": "ETH",
      "name": "Ethereum",
      "coingecko_id": "ethereum",
      "chain": "ethereum",
      "contract": null,
      "type": "major"
    },
    {
      "symbol": "KAT",
      "name": "Katana Network",
      "coingecko_id": null,
      "chain": "base",
      "contract": "0x...",
      "dexscreener_pair": "base/0x...",
      "type": "defi"
    }
  ]
}
```

#### 4. 启用 GitHub Actions

Actions → Workflows → Daily Crypto Analysis → Enable

默认每天 9:00 UTC 运行（北京时间 17:00）

### 方式二：本地运行

```bash
# 克隆仓库
git clone https://github.com/yourusername/crypto-daily-analyzer.git
cd crypto-daily-analyzer

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export GEMINI_API_KEY="your_key"

# 运行分析
python main.py
```

## 📊 推送效果

### 每日决策仪表盘

```
📊 加密市场日报 | 2026-03-03

━━━━━━━━━━━━━━━━━━━━

🎯 市场概览
• BTC: $68,725 (+4.14%) 🟢
• ETH: $2,450 (+2.8%) 🟢
• 市场情绪: 贪婪 (75) 🔥

━━━━━━━━━━━━━━━━━━━━

📈 重点代币分析

【BTC - Bitcoin】
💡 一句话结论: 强势突破 $68K 阻力，多头格局确立

📊 技术面
• 趋势: 🟢 多头排列 (MA5>MA10>MA20)
• RSI: 68 (接近超买但未过热)
• 支撑位: $66,000 / $64,000
• 阻力位: $70,000 / $72,000

📰 舆情情报
• 利好: ETF持续流入，机构增持
• 利空: 短期涨幅过大，注意回调

🎯 操作策略
• 评级: 看多 (70/100)
• 建议仓位: 5-8%
• 入场价: $67,500-68,000 (回踩)
• 止损价: $65,500 (-3.5%)
• 目标价: $71,000 (+5.5%) / $73,000 (+8.5%)

✅ 操作检查清单
[✓] 趋势向上    [✓] 量价配合    [⚠️] 不追高
[✓] 有支撑位    [✓] 舆情正面    [✓] 宏观配合

━━━━━━━━━━━━━━━━━━━━

【ETH - Ethereum】
...

━━━━━━━━━━━━━━━━━━━━

⚠️ 风险提示
本分析仅供参考，不构成投资建议。
加密货币市场波动极大，请自行承担风险。

📅 数据时间: 2026-03-03 09:00 UTC
🔍 数据来源: CoinGecko / DexScreener / 6551 OpenNews
```

## ⚙️ 内置交易纪律

| 规则 | 说明 |
|------|------|
| 严禁追高 | 乖离率超阈值（默认 7%）自动提示风险 |
| 趋势交易 | 跟随趋势，不逆势操作 |
| 精确点位 | 买入价、止损价、目标价明确 |
| 检查清单 | 每项条件以「✓/⚠️/✗」标记 |
| 仓位管理 | 根据风险等级分配仓位 |

## 🔧 配置说明

### 分析参数配置 (`config.py`)

```python
# 技术指标阈值
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
BB_THRESHOLD = 2.0
ATR_MULTIPLIER = 1.5

# 仓位建议
POSITION_SIZING = {
    'high_risk': 2,      # 高风险: 2%
    'medium_risk': 5,    # 中风险: 5%
    'low_risk': 8        # 低风险: 8%
}

# 推送设置
PUSH_TIME = "09:00"  # UTC时间
```

## 📝 自定义报告模板

编辑 `templates/report_template.md` 可自定义推送格式

支持变量：
- `{{date}}` - 日期
- `{{market_overview}}` - 市场概览
- `{{token_analyses}}` - 代币分析列表
- `{{risk_warnings}}` - 风险提示

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📜 许可证

MIT License

## ⚠️ 免责声明

本工具仅供学习和研究使用，不构成任何投资建议。
加密货币市场风险极高，投资需谨慎，自行承担风险。

---

**🌟 如果这个项目对你有帮助，请给个 Star 支持一下！**
