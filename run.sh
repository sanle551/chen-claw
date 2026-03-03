#!/bin/bash
# Crypto Daily Analyzer 控制脚本

cd /root/.openclaw/workspace/crypto-daily-analyzer

case "$1" in
  run)
    echo "🚀 运行分析..."
    python3 main.py
    ;;
  test)
    echo "🧪 测试配置..."
    python3 -c "
import json
with open('config/tokens.json') as f:
    config = json.load(f)
    print(f'✅ 配置有效，监控 {len(config[\"tokens\"])} 个代币')
"
    ;;
  install)
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt
    ;;
  cron)
    echo "📅 添加定时任务 (每天 17:00 UTC+8)..."
    (crontab -l 2>/dev/null | grep -v "crypto-daily-analyzer"; echo "0 9 * * * cd /root/.openclaw/workspace/crypto-daily-analyzer && python3 main.py >> /tmp/crypto_analyzer.log 2>&1") | crontab -
    echo "✅ 定时任务已添加"
    crontab -l | grep crypto-daily-analyzer
    ;;
  *)
    echo "📊 Crypto Daily Analyzer"
    echo ""
    echo "用法: ./run.sh [run|test|install|cron]"
    echo ""
    echo "  run     - 立即运行分析"
    echo "  test    - 测试配置"
    echo "  install - 安装依赖"
    echo "  cron    - 添加定时任务"
    ;;
esac
