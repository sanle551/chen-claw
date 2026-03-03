import os
from typing import Dict, List

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OPENNEWS_TOKEN = os.getenv('OPENNEWS_TOKEN', '')
TWITTER_TOKEN = os.getenv('TWITTER_TOKEN', '')

# Analysis Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
BB_PERIOD = 20
BB_STD = 2
ATR_PERIOD = 14

# Risk Management
MAX_POSITION_PCT = {
    'low_risk': 8,
    'medium_risk': 5,
    'high_risk': 2
}

# Technical Thresholds
PRICE_CHANGE_THRESHOLD = 5  # %
VOLUME_SPIKE_THRESHOLD = 2  # x average
LIQUIDITY_MIN_USD = 50000

# LLM Settings
GEMINI_MODEL = "gemini-2.5-pro-exp-03-25"
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0.3

# Data Sources
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest"
OPENNEWS_API_URL = "https://ai.6551.io/open"

# Push Settings
PUSH_TIME_UTC = "09:00"
