"""
Flask Web 应用主入口
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import DataFetcher
from src.analyzer import CryptoAnalyzer
from src.llm_client import LLMClient, GeminiClient
from src.notifier import TelegramNotifier
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 导入新模块
from web.auth import auth_bp, ensure_schema, get_db as auth_get_db
from web.alert_service import alerts_bp, start_alert_worker

# 创建 Flask 应用
app = Flask(__name__,
    template_folder='templates',
    static_folder='static'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-change-me'
CORS(app)

# 注册 Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(alerts_bp)

# 全局组件
data_fetcher = DataFetcher()
llm_client = GeminiClient()  # 默认使用 Gemini
analyzer = CryptoAnalyzer(llm_client)
notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID) if TELEGRAM_BOT_TOKEN else None

# 存储分析结果
analysis_cache = {}
reports_history = []

# 用户设置存储
user_settings = {}

# 初始化数据库和启动预警线程
with app.app_context():
    try:
        conn = auth_get_db()
        ensure_schema(conn)
        conn.close()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"⚠️ 数据库初始化警告: {e}")
    
    # 启动后台预警线程（可通过 DISABLE_ALERT_WORKER=1 禁用）
    start_alert_worker(app, interval_sec=300)

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表盘"""
    return render_template('dashboard.html')

@app.route('/analysis/<symbol>')
def analysis_page(symbol):
    """代币分析页面"""
    return render_template('analysis.html', symbol=symbol)

@app.route('/settings')
def settings():
    """设置页面"""
    return render_template('settings.html')

@app.route('/ai-chat')
def ai_chat():
    """AI 对话页面"""
    return render_template('ai_chat.html')

@app.route('/skills')
def skills_dashboard():
    """技能中心页面"""
    return render_template('skills.html')

# API 端点
@app.route('/api/market/overview')
def api_market_overview():
    """获取市场概览"""
    try:
        overview = data_fetcher.get_market_overview()
        return jsonify({
            'success': True,
            'data': overview,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze/<symbol>')
def api_analyze_token(symbol):
    """分析单个代币"""
    try:
        # 加载代币配置
        tokens = load_tokens()
        token = next((t for t in tokens if t['symbol'].upper() == symbol.upper()), None)
        
        if not token:
            return jsonify({'success': False, 'error': 'Token not found'}), 404
        
        # 获取数据
        price_data = data_fetcher.get_price_data(token)
        news_data = data_fetcher.get_news_data(symbol)
        
        # 分析
        result = analyzer.analyze_token(token, price_data, news_data)
        
        # 缓存结果
        analysis_cache[symbol.upper()] = {
            'data': result,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run-analysis', methods=['POST'])
def api_run_analysis():
    """运行完整分析"""
    try:
        tokens = load_tokens()
        analyses = []
        
        for token in tokens:
            try:
                price_data = data_fetcher.get_price_data(token)
                news_data = data_fetcher.get_news_data(token['symbol'])
                result = analyzer.analyze_token(token, price_data, news_data)
                analyses.append(result)
            except Exception as e:
                print(f"分析 {token['symbol']} 失败: {e}")
                continue
        
        # 生成报告
        market_overview = data_fetcher.get_market_overview()
        report = analyzer.generate_daily_report(market_overview, analyses)
        
        # 保存到历史
        report_entry = {
            'id': len(reports_history) + 1,
            'date': datetime.now().isoformat(),
            'summary': f"分析了 {len(analyses)} 个代币",
            'report': report
        }
        reports_history.append(report_entry)
        
        # 推送 Telegram
        if notifier:
            notifier.send_report(report)
        
        return jsonify({
            'success': True,
            'data': {
                'analyses_count': len(analyses),
                'report': report,
                'report_id': report_entry['id']
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports')
def api_get_reports():
    """获取历史报告"""
    return jsonify({
        'success': True,
        'data': reports_history[-20:],  # 最近20条
        'total': len(reports_history)
    })

@app.route('/api/reports/<int:report_id>')
def api_get_report(report_id):
    """获取单个报告"""
    report = next((r for r in reports_history if r['id'] == report_id), None)
    if report:
        return jsonify({'success': True, 'data': report})
    return jsonify({'success': False, 'error': 'Report not found'}), 404

@app.route('/api/tokens')
def api_get_tokens():
    """获取监控代币列表"""
    tokens = load_tokens()
    return jsonify({
        'success': True,
        'data': tokens
    })

@app.route('/api/cache/<symbol>')
def api_get_cache(symbol):
    """获取缓存的分析结果"""
    cache = analysis_cache.get(symbol.upper())
    if cache:
        return jsonify({'success': True, 'data': cache})
    return jsonify({'success': False, 'error': 'No cached data'}), 404

# === AI 聊天相关 API ===

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """AI 对话接口"""
    try:
        data = request.json
        message = data.get('message', '')
        strategy = data.get('strategy', 'comprehensive')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # 使用 LLM 生成回复
        response = llm_client.chat(message, strategy)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-ai-model', methods=['POST'])
def api_test_ai_model():
    """测试 AI 模型连接"""
    try:
        data = request.json
        provider = data.get('provider')
        api_key = data.get('api_key')
        model = data.get('model')
        base_url = data.get('base_url')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API Key is required'}), 400
        
        # 创建临时客户端测试
        test_client = LLMClient.create_client(provider, api_key, model, base_url)
        result = test_client.test_connection()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """获取/保存设置"""
    global user_settings, llm_client
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': user_settings
        })
    
    elif request.method == 'POST':
        try:
            new_settings = request.json
            user_settings.update(new_settings)
            
            # 如果有 AI 模型设置，更新客户端
            if 'ai_models' in new_settings:
                # 找到第一个启用的模型
                for provider, config in new_settings['ai_models'].items():
                    if config.get('enabled') and config.get('api_key'):
                        llm_client = LLMClient.create_client(
                            provider,
                            config['api_key'],
                            config.get('model'),
                            config.get('base_url')
                        )
                        # 更新分析器
                        global analyzer
                        analyzer = CryptoAnalyzer(llm_client)
                        break
            
            return jsonify({'success': True, 'message': 'Settings saved'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

def load_tokens():
    """加载代币配置"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'tokens.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('tokens', [])

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'js'), exist_ok=True)
    
    print("=" * 60)
    print("🚀 Crypto Daily Analyzer Web Server")
    print("=" * 60)
    print("访问地址:")
    print("  - Web界面: http://localhost:5000")
    print("  - API文档: http://localhost:5000/api/docs")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
