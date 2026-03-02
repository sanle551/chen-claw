#!/usr/bin/env node
// Market News Skill - 市场新闻聚合

async function getMarketNews() {
    // 使用多个免费 API 聚合新闻
    const sources = [
        { name: 'NewsAPI', url: 'https://newsapi.org/v2/top-headlines?category=business&apiKey=' + (process.env.NEWSAPI_KEY || 'demo') },
    ];
    
    const news = [];
    for (const source of sources) {
        try {
            const res = await fetch(source.url);
            const data = await res.json();
            if (data.articles) {
                news.push(...data.articles.slice(0, 5).map(a => ({
                    title: a.title,
                    source: source.name,
                    url: a.url,
                    publishedAt: a.publishedAt
                })));
            }
        } catch (e) {
            console.error(`${source.name} failed:`, e.message);
        }
    }
    return news;
}

module.exports = { getMarketNews };
