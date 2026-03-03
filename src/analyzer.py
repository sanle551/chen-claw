"""
分析器模块
"""
import json
from datetime import datetime
from typing import Dict, List

class CryptoAnalyzer:
    """加密货币分析器"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_token(self, token: Dict, price_data: Dict, news_data: Dict) -> Dict:
        """分析单个代币"""
        symbol = token['symbol']
        
        print(f"  - 使用 LLM 分析 {symbol}...")
        llm_result = self.llm.analyze_token(token, price_data, news_data)
        
        # 计算技术指标
        technical = self._calculate_technical_indicators(price_data)
        
        # 整合结果
        analysis = {
            'symbol': symbol,
            'name': token['name'],
            'price': price_data.get('current_price', 0),
            'change_24h': price_data.get('price_change_24h', 0),
            'market_cap': price_data.get('market_cap', 0),
            'volume': price_data.get('total_volume', 0),
            'technical_indicators': technical,
            'llm_analysis': llm_result,
            'rating': llm_result.get('rating', 50),
            'recommendation': self._get_recommendation(llm_result.get('rating', 50))
        }
        
        return analysis
    
    def _calculate_technical_indicators(self, price_data: Dict) -> Dict:
        """计算技术指标"""
        indicators = {}
        
        # 价格变化
        change_24h = price_data.get('price_change_24h', 0)
        change_7d = price_data.get('price_change_7d', 0)
        
        # 趋势判断
        if change_24h > 5 and change_7d > 10:
            indicators['trend'] = '强多头'
        elif change_24h > 0 and change_7d > 0:
            indicators['trend'] = '多头'
        elif change_24h < -5 and change_7d < -10:
            indicators['trend'] = '强空头'
        elif change_24h < 0 and change_7d < 0:
            indicators['trend'] = '空头'
        else:
            indicators['trend'] = '震荡'
        
        # 波动率
        high_24h = price_data.get('high_24h', 0)
        low_24h = price_data.get('low_24h', 0)
        current = price_data.get('current_price', 1)
        
        if high_24h and low_24h:
            volatility = ((high_24h - low_24h) / current) * 100
            indicators['volatility_24h'] = round(volatility, 2)
        
        # ATH 距离
        ath = price_data.get('ath', 0)
        ath_change = price_data.get('ath_change', 0)
        if ath:
            indicators['distance_from_ath'] = round(ath_change, 2)
        
        return indicators
    
    def _get_recommendation(self, rating: int) -> str:
        """根据评分给出建议"""
        if rating >= 80:
            return '看多'
        elif rating >= 65:
            return '谨慎看多'
        elif rating >= 50:
            return '中性'
        elif rating >= 35:
            return '谨慎看空'
        else:
            return '看空'
    
    def generate_daily_report(self, market_overview: Dict, analyses: List[Dict]) -> str:
        """生成每日报告"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 计算市场平均涨跌
        avg_change = sum(a['change_24h'] for a in analyses) / len(analyses) if analyses else 0
        
        # 统计评级分布
        bullish = sum(1 for a in analyses if a['rating'] >= 65)
        bearish = sum(1 for a in analyses if a['rating'] < 50)
        neutral = len(analyses) - bullish - bearish
        
        report = f"""📊 加密市场日报 | {date_str}

━━━━━━━━━━━━━━━━━━━━

🎯 市场概览
• BTC主导地位: {market_overview.get('btc_dominance', 0):.1f}%
• 全球市值: ${market_overview.get('total_market_cap', 0)/1e12:.2f}T
• 24h交易量: ${market_overview.get('total_volume', 0)/1e9:.1f}B
• 市值变化: {market_overview.get('market_cap_change_24h', 0):+.2f}%
• 市场情绪: {'贪婪 🔥' if avg_change > 3 else '中性 😐' if avg_change > -3 else '恐惧 ❄️'}

📊 评级分布: 🟢看多({bullish}) ⚪中性({neutral}) 🔴看空({bearish})

━━━━━━━━━━━━━━━━━━━━

"""
        
        # 添加每个代币的分析
        for analysis in analyses:
            llm = analysis.get('llm_analysis', {})
            report += self._format_token_analysis(analysis, llm)
            report += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 添加免责声明
        report += """⚠️ 风险提示
本分析仅供参考，不构成投资建议。
加密货币市场波动极大，请自行承担风险。

📅 数据时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M UTC') + """
🔍 数据来源: CoinGecko / 6551 OpenNews
        """
        
        return report
    
    def _format_token_analysis(self, analysis: Dict, llm: Dict) -> str:
        """格式化单个代币分析"""
        symbol = analysis['symbol']
        name = analysis['name']
        price = analysis['price']
        change = analysis['change_24h']
        rating = analysis['rating']
        
        emoji = '🟢' if change > 0 else '🔴' if change < 0 else '⚪'
        
        result = f"""【{symbol} - {name}】{emoji} {change:+.2f}%
💡 {llm.get('conclusion', '分析中...')}

📊 技术面
• 趋势: {analysis['technical_indicators'].get('trend', '未知')}
• 价格: ${price:,.2f}
• 市值: ${analysis['market_cap']/1e9:.2f}B
• 24h量: ${analysis['volume']/1e6:.1f}M

📰 舆情: {llm.get('sentiment', '未知')}

🎯 操作策略
• 评级: {analysis['recommendation']} ({rating}/100)
• 建议仓位: {llm.get('position_pct', 'N/A')}%
• 入场: ${llm.get('entry', 'N/A')}
• 止损: ${llm.get('stop_loss', 'N/A')} ({((llm.get('stop_loss', 0)-price)/price*100 if price else 0):.1f}%)
• 目标: ${llm.get('target', 'N/A')} ({((llm.get('target', 0)-price)/price*100 if price else 0):.1f}%)
"""
        
        # 添加检查清单
        checklist = llm.get('checklist', {})
        if checklist:
            result += "\n✅ 检查清单:\n"
            for key, value in checklist.items():
                name_map = {
                    'trend': '趋势向上',
                    'volume': '量能配合',
                    'support': '支撑有效',
                    'sentiment': '舆情正面',
                    'macro': '宏观配合'
                }
                result += f"  {value} {name_map.get(key, key)}\n"
        
        return result
