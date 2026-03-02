#!/usr/bin/env node
// Crypto Price Skill - 加密货币价格

async function getCryptoPrice(symbol) {
    // 使用 CoinGecko 免费 API
    const id = symbol.toLowerCase();
    const res = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${id}&vs_currencies=usd,cny&include_24hr_change=true`);
    return res.json();
}

async function getTrending() {
    const res = await fetch('https://api.coingecko.com/api/v3/search/trending');
    return res.json();
}

module.exports = { getCryptoPrice, getTrending };
