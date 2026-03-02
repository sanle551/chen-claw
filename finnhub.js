#!/usr/bin/env node
// Finnhub API Skill - 股票数据获取
const API_KEY = process.env.FINNHUB_API_KEY || 'demo';
const BASE_URL = 'https://finnhub.io/api/v1';

async function getQuote(symbol) {
    const res = await fetch(`${BASE_URL}/quote?symbol=${symbol}&token=${API_KEY}`);
    return res.json();
}

async function getNews(symbol) {
    const today = new Date().toISOString().split('T')[0];
    const lastWeek = new Date(Date.now() - 7*24*60*60*1000).toISOString().split('T')[0];
    const res = await fetch(`${BASE_URL}/company-news?symbol=${symbol}&from=${lastWeek}&to=${today}&token=${API_KEY}`);
    return res.json();
}

async function getFinancials(symbol) {
    const res = await fetch(`${BASE_URL}/stock/financials-reported?symbol=${symbol}&token=${API_KEY}`);
    return res.json();
}

module.exports = { getQuote, getNews, getFinancials };
