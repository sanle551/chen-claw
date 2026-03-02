# Stock Screener Skill

股票筛选工具。

## 使用

\`\`\`javascript
const screener = require('./stock-screener.js');

// 筛选价格在 100-500 之间的股票
await screener.screenStocks({ minPrice: 100, maxPrice: 500 });
\`\`\`
