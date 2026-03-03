// Crypto Daily Analyzer - 前端脚本

const API_BASE = '/api';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // 根据页面类型初始化
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        initHomePage();
    } else if (path === '/dashboard') {
        initDashboard();
    } else if (path.startsWith('/analysis/')) {
        initAnalysisPage();
    } else if (path === '/settings') {
        initSettingsPage();
    }
}

// 首页初始化
function initHomePage() {
    loadMarketOverview();
    loadTokenList();
    loadRecentReports();
    
    // 绑定运行分析按钮
    const runBtn = document.getElementById('runAnalysis');
    if (runBtn) {
        runBtn.addEventListener('click', runFullAnalysis);
    }
}

// 仪表盘初始化
function initDashboard() {
    loadDashboardData();
    
    const refreshBtn = document.getElementById('refreshData');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboardData);
    }
}

// 分析页面初始化
function initAnalysisPage() {
    if (typeof symbol !== 'undefined') {
        loadTokenAnalysis(symbol);
    }
    
    const refreshBtn = document.getElementById('refreshAnalysis');
    if (refreshBtn && typeof symbol !== 'undefined') {
        refreshBtn.addEventListener('click', () => loadTokenAnalysis(symbol));
    }
}

// 设置页面初始化
function initSettingsPage() {
    loadSettings();
    
    const saveBtn = document.getElementById('saveSettings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
}

// API 请求封装
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API 请求失败:', error);
        return { success: false, error: error.message };
    }
}

// 加载市场概览
async function loadMarketOverview() {
    const container = document.getElementById('marketOverview');
    if (!container) return;
    
    const data = await apiRequest('/market/overview');
    
    if (data.success) {
        const market = data.data;
        container.innerHTML = `
            <div class="market-stats">
                <div class="stat-item">
                    <span class="stat-label">全球市值</span>
                    <span class="stat-value">$${(market.total_market_cap / 1e12).toFixed(2)}T</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">24h交易量</span>
                    <span class="stat-value">$${(market.total_volume / 1e9).toFixed(1)}B</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">BTC主导</span>
                    <span class="stat-value">${market.btc_dominance?.toFixed(1)}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">市值变化</span>
                    <span class="stat-value ${market.market_cap_change_24h >= 0 ? 'price-up' : 'price-down'}">
                        ${market.market_cap_change_24h?.toFixed(2)}%
                    </span>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = '<p class="error">加载失败</p>';
    }
}

// 加载代币列表
async function loadTokenList() {
    const container = document.getElementById('tokenList');
    if (!container) return;
    
    const data = await apiRequest('/tokens');
    
    if (data.success) {
        const tokens = data.data;
        container.innerHTML = tokens.map(token => `
            <div class="token-card" onclick="window.location.href='/analysis/${token.symbol}'">
                <div class="token-header">
                    <span class="token-symbol">${token.symbol}</span>
                    <span class="token-type">${token.type}</span>
                </div>
                <div class="token-name">${token.name}</div>
                <div class="token-chain">${token.chain}</div>
            </div>
        `).join('');
    }
}

// 加载最近报告
async function loadRecentReports() {
    const container = document.getElementById('recentReports');
    if (!container) return;
    
    const data = await apiRequest('/reports');
    
    if (data.success && data.data.length > 0) {
        container.innerHTML = data.data.slice(-5).map(report => `
            <div class="report-item">
                <span class="report-date">${new Date(report.date).toLocaleString()}</span>
                <span class="report-summary">${report.summary}</span>
                <a href="/api/reports/${report.id}" target="_blank">查看</a>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p>暂无报告</p>';
    }
}

// 运行完整分析
async function runFullAnalysis() {
    const btn = document.getElementById('runAnalysis');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ 分析中...';
    }
    
    showNotification('🚀 开始运行完整分析...', 'info');
    
    const data = await apiRequest('/run-analysis', { method: 'POST' });
    
    if (data.success) {
        showNotification(`✅ 分析完成！分析了 ${data.data.analyses_count} 个代币`, 'success');
        loadRecentReports(); // 刷新报告列表
    } else {
        showNotification('❌ 分析失败: ' + data.error, 'error');
    }
    
    if (btn) {
        btn.disabled = false;
        btn.textContent = '🚀 立即运行分析';
    }
}

// 加载代币分析
async function loadTokenAnalysis(symbol) {
    const container = document.getElementById('analysisContent');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">正在分析...</div>';
    
    const data = await apiRequest(`/analyze/${symbol}`);
    
    if (data.success) {
        const analysis = data.data;
        const llm = analysis.llm_analysis || {};
        
        document.getElementById('tokenName').textContent = `${analysis.name} (${analysis.symbol}) 分析报告`;
        document.getElementById('analysisTime').textContent = new Date().toLocaleString();
        
        container.innerHTML = `
            <div class="analysis-section">
                <h4>💡 核心结论</h4>
                <p class="conclusion">${llm.conclusion || '暂无结论'}</p>
            </div>
            
            <div class="analysis-section">
                <h4>📊 市场数据</h4>
                <div class="data-grid">
                    <div>当前价格: <strong>$${analysis.price?.toLocaleString()}</strong></div>
                    <div>24h涨跌: <span class="${analysis.change_24h >= 0 ? 'price-up' : 'price-down'}">${analysis.change_24h?.toFixed(2)}%</span></div>
                    <div>市值: $${(analysis.market_cap / 1e9).toFixed(2)}B</div>
                    <div>评级: <strong>${analysis.recommendation}</strong> (${analysis.rating}/100)</div>
                </div>
            </div>
            
            <div class="analysis-section">
                <h4>📈 技术面</h4>
                <p>${llm.technical || '分析中...'}</p>
            </div>
            
            <div class="analysis-section">
                <h4>📰 舆情</h4>
                <p>${llm.sentiment || '分析中...'}</p>
            </div>
            
            ${llm.entry ? `
            <div class="analysis-section">
                <h4>🎯 交易策略</h4>
                <div class="strategy-box">
                    <div>建议仓位: <strong>${llm.position_pct}%</strong></div>
                    <div>入场价: <strong>$${llm.entry}</strong></div>
                    <div>止损价: <strong>$${llm.stop_loss}</strong></div>
                    <div>目标价: <strong>$${llm.target}</strong></div>
                </div>
            </div>
            ` : ''}
        `;
    } else {
        container.innerHTML = `<p class="error">分析失败: ${data.error}</p>`;
    }
}

// 加载仪表盘数据
async function loadDashboardData() {
    // 加载市场概览
    const marketStats = document.getElementById('marketStats');
    if (marketStats) {
        const data = await apiRequest('/market/overview');
        if (data.success) {
            marketStats.innerHTML = `
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-label">全球市值</div>
                        <div class="stat-value">$${(data.data.total_market_cap / 1e12).toFixed(2)}T</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">24h交易量</div>
                        <div class="stat-value">$${(data.data.total_volume / 1e9).toFixed(1)}B</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">BTC主导</div>
                        <div class="stat-value">${data.data.btc_dominance?.toFixed(1)}%</div>
                    </div>
                </div>
            `;
        }
    }
}

// 加载设置
async function loadSettings() {
    // 这里可以从服务器加载设置
}

// 保存设置
async function saveSettings() {
    showNotification('💾 设置已保存', 'success');
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') notification.style.backgroundColor = '#00C9A7';
    else if (type === 'error') notification.style.backgroundColor = '#FF4757';
    else notification.style.backgroundColor = '#2E5CFF';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
