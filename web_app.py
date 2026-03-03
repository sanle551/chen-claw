#!/usr/bin/env python3
"""
Web 版本入口文件
"""
import sys
import os

# 添加 web 目录到路径
web_dir = os.path.join(os.path.dirname(__file__), 'web')
sys.path.insert(0, web_dir)

from web.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Crypto Daily Analyzer - Web 服务器")
    print("=" * 60)
    print("访问地址:")
    print("  - Web界面: http://localhost:5000")
    print("  - API文档: http://localhost:5000/api/docs")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
