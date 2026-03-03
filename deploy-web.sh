#!/bin/bash
# Crypto Daily Analyzer Web 部署脚本

cd /root/.openclaw/workspace/crypto-daily-analyzer

case "$1" in
  install)
    echo "📦 安装 Web 依赖..."
    pip install -r requirements-web.txt
    echo "✅ 安装完成"
    ;;
  
  dev)
    echo "🚀 启动开发服务器..."
    python web_app.py
    ;;
  
  start)
    echo "🚀 启动生产服务器..."
    # 使用 Gunicorn 启动
    if command -v gunicorn &> /dev/null; then
      gunicorn -w 4 -b 0.0.0.0:5000 web_app:app --access-logfile - --error-logfile -
    else
      echo "⚠️ Gunicorn 未安装，使用 Flask 开发服务器"
      python web_app.py
    fi
    ;;
  
  docker-build)
    echo "🐳 构建 Docker 镜像..."
    docker build -t crypto-analyzer .
    ;;
  
  docker-run)
    echo "🐳 运行 Docker 容器..."
    docker run -p 5000:5000 --env-file .env crypto-analyzer
    ;;
  
  nginx)
    echo "🌐 配置 Nginx 反向代理..."
    cat > /tmp/crypto-analyzer.conf << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
    echo "配置文件已生成: /tmp/crypto-analyzer.conf"
    echo "请将其复制到 /etc/nginx/sites-available/ 并启用"
    ;;
  
  status)
    echo "📊 检查服务状态..."
    if pgrep -f "web_app.py" > /dev/null; then
      echo "✅ 服务运行中"
      curl -s http://localhost:5000/api/market/overview | head -50
    else
      echo "❌ 服务未运行"
    fi
    ;;
  
  *)
    echo "🌐 Crypto Daily Analyzer Web 部署脚本"
    echo ""
    echo "用法: ./deploy-web.sh [install|dev|start|docker-build|docker-run|nginx|status]"
    echo ""
    echo "  install       - 安装 Web 依赖"
    echo "  dev           - 启动开发服务器"
    echo "  start         - 启动生产服务器 (Gunicorn)"
    echo "  docker-build  - 构建 Docker 镜像"
    echo "  docker-run    - 运行 Docker 容器"
    echo "  nginx         - 生成 Nginx 配置"
    echo "  status        - 检查服务状态"
    echo ""
    echo "快速开始:"
    echo "  1. ./deploy-web.sh install"
    echo "  2. ./deploy-web.sh dev"
    echo "  3. 浏览器访问 http://localhost:5000"
    ;;
esac
