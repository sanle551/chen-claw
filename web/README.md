# Crypto Daily Analyzer - Web 版本

基于 Flask 的 Web 应用，支持浏览器访问和 API 调用。

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements-web.txt

# 运行开发服务器
python web_app.py

# 访问 http://localhost:5000
```

## 📁 文件结构

```
crypto-daily-analyzer/
├── web/
│   ├── __init__.py
│   ├── app.py              # Flask 主应用
│   ├── routes.py           # 路由定义
│   ├── api.py              # API 端点
│   ├── scheduler.py        # 定时任务
│   └── templates/
│       ├── index.html      # 首页
│       ├── dashboard.html  # 仪表盘
│       ├── analysis.html   # 分析报告
│       └── settings.html   # 设置页面
├── static/
│   ├── css/
│   │   └── style.css       # 样式
│   ├── js/
│   │   └── app.js          # 前端脚本
│   └── charts/             # 图表文件
└── web_app.py              # 入口文件
```

## 🔧 部署方式

### 方式1: 本地运行
```bash
python web_app.py
```

### 方式2: Docker
```bash
docker build -t crypto-analyzer .
docker run -p 5000:5000 crypto-analyzer
```

### 方式3: 云服务器
```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

## 📡 API 文档

### 获取代币分析
```
GET /api/analyze/<symbol>
```

### 获取市场概览
```
GET /api/market/overview
```

### 运行完整分析
```
POST /api/run-analysis
```

### 获取历史报告
```
GET /api/reports
```

## 🌐 访问地址

部署后访问：
- Web 界面: http://your-server:5000
- API 文档: http://your-server:5000/api/docs
