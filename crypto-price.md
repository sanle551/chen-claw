# Crypto Price Skill

加密货币价格查询。

## 使用

\`\`\`javascript
const crypto = require('./crypto-price.js');

// 获取比特币价格
await crypto.getCryptoPrice('bitcoin');

// 获取热门币种
await crypto.getTrending();
\`\`\`
