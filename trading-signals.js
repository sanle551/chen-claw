#!/usr/bin/env node
// Trading Signals Skill - 简单交易信号

async function getRSI(symbol) {
    // 使用 Yahoo Finance 数据计算 RSI
    try {
        const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1mo`);
        const data = await res.json();
        const prices = data.chart?.result?.[0]?.indicators?.quote?.[0]?.close?.filter(p => p !== null);
        if (!prices || prices.length < 14) return null;
        
        // 简化 RSI 计算
        let gains = 0, losses = 0;
        for (let i = prices.length - 14; i < prices.length; i++) {
            const change = prices[i] - prices[i-1];
            if (change > 0) gains += change;
            else losses -= change;
        }
        const rs = gains / (losses || 1);
        const rsi = 100 - (100 / (1 + rs));
        
        return {
            symbol,
            rsi: rsi.toFixed(2),
            signal: rsi > 70 ? 'OVERBOUGHT' : rsi < 30 ? 'OVERSOLD' : 'NEUTRAL'
        };
    } catch (e) {
        return null;
    }
}

module.exports = { getRSI };
