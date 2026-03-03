"""
LLM 客户端模块 - 支持多模型
"""
import requests
import json
from typing import Dict, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE

class LLMClient:
    """通用 LLM 客户端基类"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
    
    def analyze(self, prompt: str) -> str:
        """分析请求"""
        raise NotImplementedError
    
    def chat(self, message: str, context: str = "") -> str:
        """对话请求"""
        raise NotImplementedError
    
    def test_connection(self) -> Dict:
        """测试连接"""
        raise NotImplementedError
    
    @staticmethod
    def create_client(provider: str, api_key: str, model: str = None, base_url: str = None):
        """工厂方法创建客户端"""
        if provider == 'gemini':
            return GeminiClient(api_key, model or GEMINI_MODEL)
        elif provider == 'openrouter':
            return OpenRouterClient(api_key, model)
        elif provider == 'openai':
            return OpenAIClient(api_key, model)
        elif provider == 'custom':
            return CustomOpenAIClient(api_key, model, base_url)
        else:
            raise ValueError(f"Unknown provider: {provider}")


class GeminiClient(LLMClient):
    """Gemini LLM 客户端"""
    
    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key or GEMINI_API_KEY, model or GEMINI_MODEL)
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}"
    
    def analyze(self, prompt: str) -> str:
        """发送分析请求"""
        try:
            url = f"{self.base_url}:generateContent"
            headers = {'Content-Type': 'application/json'}
            
            data = {
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'maxOutputTokens': LLM_MAX_TOKENS,
                    'temperature': LLM_TEMPERATURE
                }
            }
            
            response = requests.post(
                url, headers=headers, params={'key': self.api_key},
                json=data, timeout=60
            )
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"API 错误: {result}"
                
        except Exception as e:
            return f"请求失败: {e}"
    
    def chat(self, message: str, strategy: str = "comprehensive") -> str:
        """对话请求"""
        # 构建策略特定的系统提示
        strategy_prompts = {
            'trend': '你是一位趋势交易专家（猎豹策略），专注于技术分析、动量交易和短线机会。',
            'value': '你是一位价值投资专家（树懒策略），专注于基本面分析、长期持有和风险排除。',
            'macro': '你是一位宏观择时专家（猫头鹰策略），专注于市场周期、风险控制和仓位管理。',
            'arbitrage': '你是一位套利交易专家（鲨鱼策略），专注于市场微观结构、价差套利和聪明钱动向。',
            'comprehensive': '你是一位全面的加密货币分析师，结合多种策略提供平衡的分析建议。'
        }
        
        system_prompt = strategy_prompts.get(strategy, strategy_prompts['comprehensive'])
        
        prompt = f"""{system_prompt}

用户问题: {message}

请提供详细、专业的分析和建议，包括：
1. 当前市场状况分析
2. 具体的技术/基本面观点
3. 明确的操作建议（入场、止损、止盈）
4. 风险提示

请用中文回答，格式清晰。"""
        
        return self.analyze(prompt)
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            result = self.analyze("Say 'Connection successful' if you can hear me.")
            if 'successful' in result.lower() or '成功' in result:
                return {'success': True, 'message': '连接正常'}
            return {'success': True, 'message': result[:50]}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class OpenRouterClient(LLMClient):
    """OpenRouter 客户端"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(api_key, model)
        self.base_url = "https://openrouter.ai/api/v1"
    
    def analyze(self, prompt: str) -> str:
        """发送分析请求"""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://crypto-analyzer.local',
                'X-Title': 'Crypto Daily Analyzer'
            }
            
            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': LLM_MAX_TOKENS,
                'temperature': LLM_TEMPERATURE
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return f"API 错误: {result}"
                
        except Exception as e:
            return f"请求失败: {e}"
    
    def chat(self, message: str, strategy: str = "comprehensive") -> str:
        """对话请求"""
        strategy_prompts = {
            'trend': '趋势交易专家',
            'value': '价值投资专家',
            'macro': '宏观择时专家',
            'arbitrage': '套利交易专家',
            'comprehensive': '全面分析师'
        }
        
        system_msg = f"你是一位专业的加密货币{strategy_prompts.get(strategy, '分析师')}。"
        
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': LLM_MAX_TOKENS,
                'temperature': LLM_TEMPERATURE
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            return f"错误: {result}"
            
        except Exception as e:
            return f"请求失败: {e}"
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            result = self.analyze("Hello")
            return {'success': True, 'message': '连接正常' if len(result) > 0 else '返回空'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class OpenAIClient(LLMClient):
    """OpenAI 官方客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model)
        self.base_url = "https://api.openai.com/v1"
    
    def analyze(self, prompt: str) -> str:
        """发送分析请求"""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': LLM_MAX_TOKENS,
                'temperature': LLM_TEMPERATURE
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            return f"错误: {result}"
            
        except Exception as e:
            return f"请求失败: {e}"
    
    def chat(self, message: str, strategy: str = "comprehensive") -> str:
        """对话请求"""
        return self.analyze(message)
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            result = self.analyze("Hi")
            return {'success': True, 'message': '连接正常'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class CustomOpenAIClient(LLMClient):
    """自定义 OpenAI 兼容 API 客户端"""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        super().__init__(api_key, model)
        self.base_url = base_url.rstrip('/')
    
    def analyze(self, prompt: str) -> str:
        """发送分析请求"""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': LLM_MAX_TOKENS,
                'temperature': LLM_TEMPERATURE
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            return f"错误: {result}"
            
        except Exception as e:
            return f"请求失败: {e}"
    
    def chat(self, message: str, strategy: str = "comprehensive") -> str:
        """对话请求"""
        return self.analyze(message)
    
    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            result = self.analyze("Test")
            return {'success': True, 'message': '连接正常'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# 为了保持向后兼容
GeminiClient = GeminiClient
