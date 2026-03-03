"""
数据获取模块
"""
import requests
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from config import (
    COINGECKO_API_URL, DEXSCREENER_API_URL,
    OPENNEWS_API_URL, OPENNEWS_TOKEN, TWITTER_TOKEN
)

class DataFetcher:
    """数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        try:
            url = f"{COINGECKO_API_URL}/global"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            return {
                'total_market_cap': data.get('data', {}).get('total_market_cap', {}).get('usd', 0),
                'total_volume': data.get('data', {}).get('total_volume', {}).get('usd', 0),
                'btc_dominance': data.get('data', {}).get('market_cap_percentage', {}).get('btc', 0),
                'market_cap_change_24h': data.get('data', {}).get('market_cap_change_percentage_24h_usd', 0)
            }
        except Exception as e:
            print(f"获取市场概览失败: {e}")
            return {}
    
    def get_price_data(self, token: Dict) -> Dict:
        """获取代币价格数据"""
        coingecko_id = token.get('coingecko_id')
        
        if coingecko_id:
            return self._get_coingecko_data(coingecko_id)
        else:
            # 使用 DexScreener 获取链上代币数据
            pair_address = token.get('dexscreener_pair')
            if pair_address:
                return self._get_dexscreener_data(pair_address)
        
        return {}
    
    def _get_coingecko_data(self, coingecko_id: str) -> Dict:
        """从 CoinGecko 获取数据"""
        try:
            url = f"{COINGECKO_API_URL}/coins/{coingecko_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            }
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            market_data = data.get('market_data', {})
            return {
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'total_supply': market_data.get('total_supply', 0),
                'high_24h': market_data.get('high_24h', {}).get('usd', 0),
                'low_24h': market_data.get('low_24h', {}).get('usd', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'ath_change': market_data.get('ath_change_percentage', 0)
            }
        except Exception as e:
            print(f"获取 CoinGecko 数据失败: {e}")
            return {}
    
    def _get_dexscreener_data(self, pair_address: str) -> Dict:
        """从 DexScreener 获取数据"""
        try:
            url = f"{DEXSCREENER_API_URL}/dex/pairs/{pair_address}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            pair = data.get('pairs', [{}])[0]
            return {
                'current_price': float(pair.get('priceUsd', 0)),
                'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                'market_cap': float(pair.get('marketCap', 0)),
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                'dex': pair.get('dexId', ''),
                'chain': pair.get('chainId', '')
            }
        except Exception as e:
            print(f"获取 DexScreener 数据失败: {e}")
            return {}
    
    def get_news_data(self, symbol: str) -> Dict:
        """获取新闻数据"""
        try:
            url = f"{OPENNEWS_API_URL}/news_search"
            headers = {
                'Authorization': f'Bearer {OPENNEWS_TOKEN}',
                'Content-Type': 'application/json'
            }
            data = {
                'q': f'{symbol} Bitcoin crypto',
                'limit': 5
            }
            response = self.session.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            return {
                'articles': result.get('data', []),
                'count': len(result.get('data', []))
            }
        except Exception as e:
            print(f"获取新闻数据失败: {e}")
            return {'articles': [], 'count': 0}
