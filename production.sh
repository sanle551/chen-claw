#!/bin/bash
# Crypto Daily Analyzer - 生产部署启动脚本
# 服务器: 43.134.16.249

APP_DIR="/root/.openclaw/workspace/crypto-daily-analyzer"
LOG_DIR="/var/log/crypto-analyzer"
PID_FILE="/tmp/crypto-analyzer.pid"

cd $APP_DIR

# 创建日志目录
mkdir -p $LOG_DIR

case "$1" in
  start)
    echo "🚀 启动 Crypto Daily Analyzer (生产模式)..."
    echo "访问地址: http://43.134.16.249:5000"
    echo ""
    
    # 检查是否已在运行
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
      echo "⚠️ 服务已在运行 (PID: $(cat $PID_FILE))"
      echo "访问: http://43.134.16.249:5000"
      exit 0
    fi
    
    # 启动 Gunicorn
    nohup gunicorn \
      -w 4 \
      -b 0.0.0.0:5000 \
      --access-logfile $LOG_DIR/access.log \
      --error-logfile $LOG_DIR/error.log \
      --pid $PID_FILE \
      --daemon \
      web_app:app &
    
    sleep 2
    
    if [ -f $PID_FILE ]; then
      echo "✅ 启动成功!"
      echo "PID: $(cat $PID_FILE)"
      echo "访问: http://43.134.16.249:5000"
      echo "日志: $LOG_DIR/"
    else
      echo "❌ 启动失败，请检查日志"
      tail -20 $LOG_DIR/error.log
    fi
    ;;
  
  stop)
    echo "🛑 停止服务..."
    if [ -f $PID_FILE ]; then
      kill $(cat $PID_FILE) 2>/dev/null
      rm -f $PID_FILE
      echo "✅ 已停止"
    else
      echo "⚠️ 服务未运行"
    fi
    ;;
  
  restart)
    echo "🔄 重启服务..."
    $0 stop
    sleep 2
    $0 start
    ;;
  
  status)
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
      echo "✅ 服务运行中"
      echo "PID: $(cat $PID_FILE)"
      echo "访问: http://43.134.16.249:5000"
      echo ""
      echo "最近日志:"
      tail -5 $LOG_DIR/error.log 2>/dev/null || echo "暂无日志"
    else
      echo "❌ 服务未运行"
    fi
    ;;
  
  logs)
    echo "📋 查看日志 (按 Ctrl+C 退出)..."
    tail -f $LOG_DIR/error.log
    ;;
  
  test)
    echo "🧪 测试服务..."
    curl -s http://43.134.16.249:5000/api/market/overview | python3 -m json.tool
    ;;
  
  *)
    echo "🌐 Crypto Daily Analyzer - 生产部署管理"
    echo "服务器: 43.134.16.249"
    echo ""
    echo "用法: ./production.sh [start|stop|restart|status|logs|test]"
    echo ""
    echo "  start    - 启动服务"
    echo "  stop     - 停止服务"
    echo "  restart  - 重启服务"
    echo "  status   - 查看状态"
    echo "  logs     - 查看日志"
    echo "  test     - 测试API"
    echo ""
    echo "访问地址: http://43.134.16.249:5000"
    ;;
esac
