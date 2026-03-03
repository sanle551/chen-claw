"""
🤖 AI模型配置中心 - 最新模型支持
包含：Gemini 3.1 Pro, GPT-5.2, Claude 3.5 等最新模型
"""

# 最新AI模型配置
LATEST_AI_MODELS = {
    "gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "models": {
            "gemini-3.1-pro": {
                "name": "Gemini 3.1 Pro",
                "tags": ["推理", "多模态", "最新"],
                "context": 2000000,  # 2M上下文
                "description": "Google最新旗舰模型，最强推理能力"
            },
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "tags": ["推理", "多模态"],
                "context": 1000000,
                "description": "上一代旗舰，依然强大"
            },
            "gemini-2.0-flash": {
                "name": "Gemini 2.0 Flash",
                "tags": ["快速", "多模态"],
                "context": 1000000,
                "description": "快速响应，适合实时应用"
            },
            "gemini-2.0-pro": {
                "name": "Gemini 2.0 Pro",
                "tags": ["推理", "多模态"],
                "context": 2000000,
                "description": "Pro级别性能"
            }
        }
    },
    
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": {
            "gpt-5.2": {
                "name": "GPT-5.2",
                "tags": ["最新", "推理", "多模态"],
                "context": 256000,
                "description": "OpenAI最新旗舰模型"
            },
            "gpt-5": {
                "name": "GPT-5",
                "tags": ["推理", "多模态"],
                "context": 256000,
                "description": "GPT-5系列基础版"
            },
            "gpt-4o": {
                "name": "GPT-4o",
                "tags": ["多模态"],
                "context": 128000,
                "description": "全模态旗舰"
            },
            "gpt-4o-mini": {
                "name": "GPT-4o Mini",
                "tags": ["快速", "低成本"],
                "context": 128000,
                "description": "高性价比"
            },
            "o1": {
                "name": "o1",
                "tags": ["推理"],
                "context": 200000,
                "description": "推理专用模型"
            },
            "o1-preview": {
                "name": "o1 Preview",
                "tags": ["推理", "预览"],
                "context": 128000,
                "description": "o1预览版"
            },
            "o1-mini": {
                "name": "o1 Mini",
                "tags": ["推理", "快速"],
                "context": 128000,
                "description": "轻量推理模型"
            }
        }
    },
    
    "openrouter": {
        "name": "OpenRouter (聚合)",
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "google/gemini-3.1-pro": {
                "name": "Gemini 3.1 Pro (OpenRouter)",
                "tags": ["推理", "多模态", "最新"],
                "context": 2000000
            },
            "google/gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "tags": ["推理", "多模态"],
                "context": 1000000
            },
            "openai/gpt-5.2": {
                "name": "GPT-5.2 (OpenRouter)",
                "tags": ["最新", "推理", "多模态"],
                "context": 256000
            },
            "openai/gpt-5": {
                "name": "GPT-5",
                "tags": ["推理", "多模态"],
                "context": 256000
            },
            "anthropic/claude-3.5-sonnet": {
                "name": "Claude 3.5 Sonnet",
                "tags": ["推理", "多模态"],
                "context": 200000
            },
            "anthropic/claude-3-opus": {
                "name": "Claude 3 Opus",
                "tags": ["推理", "多模态"],
                "context": 200000
            },
            "meta-llama/llama-3.3-70b": {
                "name": "Llama 3.3 70B",
                "tags": ["开源", "推理"],
                "context": 128000
            },
            "deepseek/deepseek-chat": {
                "name": "DeepSeek V3",
                "tags": ["推理", "中文优化"],
                "context": 64000
            }
        }
    },
    
    "anthropic": {
        "name": "Anthropic (直连)",
        "base_url": "https://api.anthropic.com/v1",
        "models": {
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "tags": ["推理", "多模态", "最新"],
                "context": 200000
            },
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "tags": ["推理", "多模态"],
                "context": 200000
            },
            "claude-3-haiku-20240307": {
                "name": "Claude 3 Haiku",
                "tags": ["快速"],
                "context": 200000
            }
        }
    },
    
    "custom": {
        "name": "自定义 API",
        "base_url": "",
        "models": {
            "custom": {
                "name": "自定义模型",
                "tags": ["自定义"],
                "context": 128000,
                "description": "任意 OpenAI 兼容 API"
            }
        }
    }
}

# 模型推荐配置
RECOMMENDED_MODELS = {
    "analysis": "gemini-3.1-pro",  # 分析用最强模型
    "chat": "gemini-2.0-flash",     # 聊天用快速模型
    "code": "gpt-5.2",              # 编程用最新模型
    "economy": "gpt-4o-mini"        # 经济型选择
}

# 模型能力标签样式
TAG_STYLES = {
    "最新": {"bg": "#00c9a7", "color": "#000"},
    "推理": {"bg": "#ffa502", "color": "#000"},
    "多模态": {"bg": "#9b59b6", "color": "#fff"},
    "快速": {"bg": "#3498db", "color": "#fff"},
    "开源": {"bg": "#2ecc71", "color": "#000"},
    "中文优化": {"bg": "#e74c3c", "color": "#fff"},
    "自定义": {"bg": "#95a5a6", "color": "#000"}
}

def get_model_info(provider: str, model_id: str) -> dict:
    """获取模型信息"""
    provider_config = LATEST_AI_MODELS.get(provider, {})
    models = provider_config.get("models", {})
    return models.get(model_id, {})

def get_all_models() -> dict:
    """获取所有模型列表"""
    result = {}
    for provider, config in LATEST_AI_MODELS.items():
        result[provider] = {
            "name": config["name"],
            "models": list(config["models"].keys())
        }
    return result

def get_latest_models() -> list:
    """获取标记为'最新'的模型"""
    latest = []
    for provider, config in LATEST_AI_MODELS.items():
        for model_id, model_info in config["models"].items():
            if "最新" in model_info.get("tags", []):
                latest.append({
                    "provider": provider,
                    "id": model_id,
                    **model_info
                })
    return latest
