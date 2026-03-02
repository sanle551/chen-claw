#!/usr/bin/env node
// Stock Screener Skill - 股票筛选

const DEFAULT_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'];

async function screenStocks(criteria = {}) {
    const { minPrice = 0, maxPrice = 10000, sector } = criteria;
    
    // 使用 Yahoo Finance 免费 API (通过快速查询)
    const results = [];
    for (const symbol of DEFAULT_STOCKS) {
        try {
            const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`);
            const data = await res.json();
            if (data.chart?.result?.[0]) {
                const meta = data.chart.result[0].meta;
                const price = meta.regularMarketPrice;
                if (price >= minPrice && price <= maxPrice) {
                    results.push({
                        symbol,
                        price,
                        currency: meta.currency,
                        exchange: meta.exchangeName
                    });
                }
            }
        } catch (e) {
            // 忽略错误
        }
    }
    return results;
}

module.exports = { screenStocks };
