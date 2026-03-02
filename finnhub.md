# Finnhub Skill

实时股票数据、新闻、财务报表。

## 使用

\`\`\`javascript
const finnhub = require('./finnhub.js');

// 获取股票报价
await finnhub.getQuote('AAPL');

// 获取公司新闻
await finnhub.getNews('TSLA');

// 获取财务报表
await finnhub.getFinancials('MSFT');
\`\`\`

## 环境变量

- FINNHUB_API_KEY - API 密钥 (从 finnhub.io 获取免费密钥)
