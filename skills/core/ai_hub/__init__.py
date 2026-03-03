"""
🤖 AI分析整合技能
多模型对比分析 + 策略回测 + 智能仓位建议
"""
import json
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

LOGGER = logging.getLogger("ai_hub")

class AnalysisStrategy(Enum):
    """分析策略类型"""
    TREND_FOLLOWING = "trend"        # 趋势跟随
    VALUE_INVESTING = "value"        # 价值投资
    MACRO_TIMING = "macro"           # 宏观择时
    ARBITRAGE = "arbitrage"          # 套利博弈
    COMPREHENSIVE = "comprehensive"  # 综合分析

@dataclass
class AIModelResult:
    """AI模型分析结果"""
    model_name: str
    provider: str
    conclusion: str
    rating: int  # 0-100
    confidence: float  # 0-1
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    position_pct: float
    reasoning: str
    timestamp: str

@dataclass
class ConsensusResult:
    """多模型共识结果"""
    avg_rating: float
    consensus_conclusion: str
    confidence_score: float
    divergent_views: List[str]
    recommended_strategy: str
    position_sizing: Dict[str, float]
    risk_level: str  # low/medium/high


class AIModelHub:
    """AI模型整合中心"""
    
    def __init__(self):
        self.models: Dict[str, Dict] = {}
        self.results_cache: Dict[str, List[AIModelResult]] = {}
        self.consensus_history: Dict[str, List[ConsensusResult]] = {}
        
    def register_model(self, name: str, provider: str, 
                      client: Callable, weight: float = 1.0):
        """注册AI模型
        
        Args:
            name: 模型名称
            provider: 提供商 (gemini/openai/openrouter)
            client: 模型客户端函数
            weight: 权重 (用于共识计算)
        """
        self.models[name] = {
            "name": name,
            "provider": provider,
            "client": client,
            "weight": weight,
            "enabled": True
        }
        LOGGER.info(f"注册AI模型: {name} ({provider})")
        
    def analyze_with_all_models(self, symbol: str, 
                                market_data: Dict,
                                strategy: AnalysisStrategy = AnalysisStrategy.COMPREHENSIVE) -> List[AIModelResult]:
        """使用所有启用的模型进行分析
        
        Args:
            symbol: 代币符号
            market_data: 市场数据
            strategy: 分析策略
            
        Returns:
            各模型的分析结果列表
        """
        results = []
        
        for model_name, model_info in self.models.items():
            if not model_info.get("enabled"):
                continue
                
            try:
                result = self._analyze_with_model(
                    model_info, symbol, market_data, strategy
                )
                results.append(result)
            except Exception as e:
                LOGGER.error(f"模型 {model_name} 分析失败: {e}")
                
        # 缓存结果
        cache_key = f"{symbol}_{strategy.value}_{datetime.now().strftime('%Y%m%d%H')}"
        self.results_cache[cache_key] = results
        
        return results
        
    def _analyze_with_model(self, model_info: Dict, symbol: str,
                           market_data: Dict, strategy: AnalysisStrategy) -> AIModelResult:
        """使用单个模型分析"""
        
        # 构建提示词
        prompt = self._build_analysis_prompt(symbol, market_data, strategy)
        
        # 调用模型
        client = model_info["client"]
        response = client(prompt)
        
        # 解析结果
        parsed = self._parse_model_response(response)
        
        return AIModelResult(
            model_name=model_info["name"],
            provider=model_info["provider"],
            conclusion=parsed.get("conclusion", ""),
            rating=parsed.get("rating", 50),
            confidence=parsed.get("confidence", 0.5),
            entry_price=parsed.get("entry_price"),
            stop_loss=parsed.get("stop_loss"),
            take_profit=parsed.get("take_profit"),
            position_pct=parsed.get("position_pct", 5.0),
            reasoning=parsed.get("reasoning", ""),
            timestamp=datetime.now().isoformat()
        )
        
    def _build_analysis_prompt(self, symbol: str, market_data: Dict, 
                              strategy: AnalysisStrategy) -> str:
        """构建分析提示词"""
        
        strategy_desc = {
            AnalysisStrategy.TREND_FOLLOWING: "趋势跟随策略：关注动量、突破、技术信号",
            AnalysisStrategy.VALUE_INVESTING: "价值投资策略：关注基本面、长期价值、风险排除",
            AnalysisStrategy.MACRO_TIMING: "宏观择时策略：关注市场周期、风险控制、仓位管理",
            AnalysisStrategy.ARBITRAGE: "套利博弈策略：关注市场微观结构、价差、聪明钱动向",
            AnalysisStrategy.COMPREHENSIVE: "综合分析：结合多种视角给出平衡建议"
        }
        
        prompt = f"""作为专业的加密货币分析师，请基于以下信息对 {symbol} 进行分析。

【分析策略】
{strategy_desc.get(strategy, strategy.value)}

【市场数据】
- 当前价格: ${market_data.get('current_price', 'N/A')}
- 24h涨跌: {market_data.get('change_24h', 'N/A')}%
- 市值: ${market_data.get('market_cap', 'N/A')}
- 24h交易量: ${market_data.get('volume', 'N/A')}

【请提供以下分析】（以JSON格式输出）
{{
    "conclusion": "一句话核心结论（15字以内）",
    "rating": 75,  // 0-100分
    "confidence": 0.8,  // 0-1
    "entry_price": 68000,
    "stop_loss": 65000,
    "take_profit": 75000,
    "position_pct": 5,  // 建议仓位百分比
    "reasoning": "详细分析逻辑..."
}}"""
        
        return prompt
        
    def _parse_model_response(self, response: str) -> Dict:
        """解析模型响应"""
        try:
            # 尝试提取JSON
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            else:
                json_str = response
                
            return json.loads(json_str)
        except:
            # 解析失败返回默认值
            return {
                "conclusion": response[:100] if response else "分析失败",
                "rating": 50,
                "confidence": 0.5
            }
            
    def calculate_consensus(self, symbol: str, 
                           results: List[AIModelResult] = None) -> ConsensusResult:
        """计算多模型共识
        
        Args:
            symbol: 代币符号
            results: 如果提供则使用，否则从缓存获取
            
        Returns:
            共识结果
        """
        if results is None:
            cache_key = f"{symbol}_comprehensive_{datetime.now().strftime('%Y%m%d%H')}"
            results = self.results_cache.get(cache_key, [])
            
        if not results:
            return ConsensusResult(
                avg_rating=50,
                consensus_conclusion="无分析数据",
                confidence_score=0,
                divergent_views=[],
                recommended_strategy="观望",
                position_sizing={},
                risk_level="high"
            )
            
        # 计算加权平均评分
        total_weight = 0
        weighted_rating = 0
        
        for r in results:
            weight = self.models.get(r.model_name, {}).get("weight", 1.0)
            weighted_rating += r.rating * weight * r.confidence
            total_weight += weight * r.confidence
            
        avg_rating = weighted_rating / total_weight if total_weight > 0 else 50
        
        # 计算分歧度
        ratings = [r.rating for r in results]
        rating_std = (sum((r - avg_rating)**2 for r in ratings) / len(ratings))**0.5
        
        # 判断共识
        if rating_std < 10:
            consensus = "强共识"
        elif rating_std < 20:
            consensus = "中等共识"
        else:
            consensus = "分歧较大"
            
        # 找出分歧观点
        divergent = []
        for r in results:
            if abs(r.rating - avg_rating) > 20:
                divergent.append(f"{r.model_name}: {r.conclusion}")
                
        # 推荐策略
        if avg_rating >= 80:
            recommended = "积极做多"
            risk = "medium"
        elif avg_rating >= 60:
            recommended = "谨慎做多"
            risk = "medium"
        elif avg_rating >= 40:
            recommended = "观望"
            risk = "medium"
        else:
            recommended = "回避"
            risk = "high"
            
        # 仓位建议
        position = {
            "conservative": min(avg_rating / 20, 5),
            "moderate": min(avg_rating / 15, 8),
            "aggressive": min(avg_rating / 10, 15)
        }
        
        consensus_result = ConsensusResult(
            avg_rating=avg_rating,
            consensus_conclusion=consensus,
            confidence_score=1 - (rating_std / 50),  # 分歧越小置信度越高
            divergent_views=divergent,
            recommended_strategy=recommended,
            position_sizing=position,
            risk_level=risk
        )
        
        # 保存历史
        if symbol not in self.consensus_history:
            self.consensus_history[symbol] = []
        self.consensus_history[symbol].append(consensus_result)
        
        return consensus_result
        
    def backtest_strategy(self, symbol: str, strategy: AnalysisStrategy,
                         start_date: str, end_date: str) -> Dict:
        """策略回测
        
        Args:
            symbol: 代币符号
            strategy: 策略类型
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            回测结果
        """
        # 这里应该调用历史数据进行回测
        # 示例返回结构
        return {
            "symbol": symbol,
            "strategy": strategy.value,
            "period": f"{start_date} ~ {end_date}",
            "total_return": 15.5,
            "max_drawdown": -8.2,
            "sharpe_ratio": 1.2,
            "win_rate": 0.65,
            "trade_count": 20,
            "avg_profit_per_trade": 0.78
        }


class SmartPositionAdvisor:
    """智能仓位建议器"""
    
    def __init__(self, ai_hub: AIModelHub):
        self.ai_hub = ai_hub
        
    def advise_position(self, symbol: str, 
                       portfolio_value: float,
                       risk_tolerance: str = "moderate") -> Dict:
        """提供智能仓位建议
        
        Args:
            symbol: 代币符号
            portfolio_value: 投资组合总价值
            risk_tolerance: 风险承受度 (conservative/moderate/aggressive)
            
        Returns:
            仓位建议
        """
        # 获取共识
        consensus = self.ai_hub.calculate_consensus(symbol)
        
        # 根据风险承受度调整
        base_position = consensus.position_sizing.get(risk_tolerance, 5)
        
        # 根据信心度调整
        confidence_adjustment = consensus.confidence_score
        adjusted_position = base_position * confidence_adjustment
        
        # 计算具体金额
        position_value = portfolio_value * (adjusted_position / 100)
        
        return {
            "symbol": symbol,
            "recommended_position_pct": round(adjusted_position, 2),
            "recommended_position_value": round(position_value, 2),
            "portfolio_percentage": round(adjusted_position, 2),
            "max_single_position_pct": 15 if risk_tolerance == "aggressive" else (10 if risk_tolerance == "moderate" else 5),
            "risk_level": consensus.risk_level,
            "confidence": round(consensus.confidence_score, 2),
            "rationale": f"基于{consensus.consensus_conclusion}，建议{risk_tolerance}仓位"
        }


# 全局实例
ai_hub = AIModelHub()
position_advisor = SmartPositionAdvisor(ai_hub)

# 便捷函数
def get_ai_hub() -> AIModelHub:
    """获取AI Hub实例"""
    return ai_hub

def analyze_consensus(symbol: str, market_data: Dict) -> ConsensusResult:
    """快速共识分析"""
    results = ai_hub.analyze_with_all_models(symbol, market_data)
    return ai_hub.calculate_consensus(symbol, results)

def get_position_advice(symbol: str, portfolio_value: float) -> Dict:
    """获取仓位建议"""
    return position_advisor.advise_position(symbol, portfolio_value)
