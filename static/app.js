/**
 * 新兴支柱产业追踪 - 前端逻辑
 * 每产业3只代表性股票，卡片式展示
 */

const API_BASE = '';
let currentIndustry = null;

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', () => {
    loadIndustries();
    updateTime();
    setInterval(updateTime, 1000);
});

function updateTime() {
    const now = new Date();
    const opts = { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit', hour12:false };
    const el = document.getElementById('navTime');
    if (el) el.textContent = now.toLocaleString('zh-CN', opts);
}

// ============ 产业列表 ============
async function loadIndustries() {
    try {
        const res = await fetch(`${API_BASE}/api/industries`);
        const data = await res.json();
        renderIndustryGrid(data.industries);
    } catch (e) {
        document.getElementById('industryGrid').innerHTML =
            '<div style="grid-column:1/-1;text-align:center;padding:60px;color:#86868b;">加载失败，请刷新重试</div>';
    }
}

function renderIndustryGrid(industries) {
    const grid = document.getElementById('industryGrid');
    grid.innerHTML = industries.map((ind, i) => `
        <div class="industry-card" style="--card-gradient:${ind.gradient}; animation:fadeIn 0.4s ease ${i*0.06}s both;" onclick="showDetail('${ind.id}')">
            <span class="card-icon">${ind.icon}</span>
            <div class="card-name">${ind.name}</div>
            <div class="card-subtitle">${ind.subtitle}</div>
            <div class="card-desc">${ind.description}</div>
            <div class="card-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg></div>
        </div>
    `).join('');
}

// ============ 页面切换 ============
function showHome() {
    document.getElementById('homePage').style.display = '';
    document.getElementById('detailPage').style.display = 'none';
    currentIndustry = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function showDetail(industryId) {
    currentIndustry = industryId;
    try {
        const res = await fetch(`${API_BASE}/api/industries`);
        const data = await res.json();
        const ind = data.industries.find(i => i.id === industryId);
        if (ind) {
            document.getElementById('detailIcon').textContent = ind.icon;
            document.getElementById('detailTitle').textContent = ind.name;
        }
    } catch (e) {}

    document.getElementById('homePage').style.display = 'none';
    document.getElementById('detailPage').style.display = '';
    window.scrollTo({ top: 0 });
    loadStocks(industryId);
    loadNews(industryId);
}

// ============ 股票数据 ============
async function loadStocks(industryId) {
    const aContainer = document.getElementById('aStockCards');
    const hkContainer = document.getElementById('hkStockCards');
    aContainer.innerHTML = '<div class="loading-skeleton"><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div></div>';

    try {
        const res = await fetch(`${API_BASE}/api/industry/${industryId}/stocks`);
        const data = await res.json();

        document.getElementById('aStockCount').textContent = data.a_count || 0;
        document.getElementById('hkStockCount').textContent = data.hk_count || 0;
        document.getElementById('detailUpdateTime').textContent = '更新: ' + (data.update_time || '');

        const hkSection = document.getElementById('hkSection');
        hkSection.style.display = (data.hk_stocks && data.hk_stocks.length > 0) ? '' : 'none';

        aContainer.innerHTML = (data.a_stocks || []).map(s => renderStockCard(s)).join('');
        hkContainer.innerHTML = (data.hk_stocks || []).map(s => renderStockCard(s, true)).join('');
    } catch (e) {
        aContainer.innerHTML = '<div style="padding:24px;color:#86868b;text-align:center">加载失败</div>';
    }
}

function renderStockCard(s, isHK = false) {
    const changeClass = s.change_pct > 0 ? 'up' : s.change_pct < 0 ? 'down' : 'flat';
    const changeStr = s.change_pct != null
        ? (s.change_pct > 0 ? '+' : '') + s.change_pct.toFixed(2) + '%'
        : '--';
    const priceStr = s.price != null ? s.price.toFixed(2) : '--';
    const noteStr = s.note ? `<span class="stock-note">${s.note}</span>` : '';

    return `
    <div class="stock-card ${changeClass}">
        <div class="stock-card-header">
            <div class="stock-name-row">
                <strong class="stock-name">${s.name || '--'}</strong>
                ${noteStr}
            </div>
            <div class="stock-code">${isHK ? 'HK' : ''}${s.code || '--'}</div>
        </div>
        <div class="stock-card-price">
            <span class="stock-price">${priceStr}</span>
            <span class="stock-change ${changeClass}">${changeStr}</span>
        </div>
        <div class="stock-card-metrics">
            <div class="metric"><span class="metric-label">PE</span><span class="metric-value">${s.pe != null ? s.pe.toFixed(2) : '--'}</span></div>
            <div class="metric"><span class="metric-label">PS</span><span class="metric-value">${s.ps != null ? s.ps.toFixed(2) : '--'}</span></div>
            <div class="metric"><span class="metric-label">市值</span><span class="metric-value">${s.market_cap || '--'}</span></div>
        </div>
    </div>`;
}

function refreshStocks() {
    if (!currentIndustry) return;
    const btn = document.getElementById('stockRefreshBtn');
    btn.classList.add('spinning');
    setTimeout(() => btn.classList.remove('spinning'), 800);
    loadStocks(currentIndustry);
}

// ============ 资讯 ============
async function loadNews(industryId) {
    const container = document.getElementById('newsList');
    container.innerHTML = '<div class="loading-skeleton"><div class="skeleton-line"></div><div class="skeleton-line short"></div><div class="skeleton-line"></div></div>';

    try {
        const res = await fetch(`${API_BASE}/api/industry/${industryId}/news`);
        const data = await res.json();
        renderNews(data.news || []);
    } catch (e) {
        container.innerHTML = '<div style="padding:24px;color:#86868b;text-align:center">加载失败</div>';
    }
}

function renderNews(news) {
    const container = document.getElementById('newsList');
    if (!news.length) {
        container.innerHTML = '<div style="padding:24px;color:#86868b;text-align:center">暂无资讯</div>';
        return;
    }
    container.innerHTML = news.map(n => `
        <a class="news-item" href="${n.url || '#'}" target="_blank" rel="noopener">
            <div class="news-title">${n.title || '无标题'}</div>
            <div class="news-meta">
                <span class="news-source">${n.source || ''}</span>
                <span class="news-time">${n.time || ''}</span>
            </div>
        </a>
    `).join('');
}

function refreshNews() {
    if (!currentIndustry) return;
    const btn = document.getElementById('newsRefreshBtn');
    btn.classList.add('spinning');
    setTimeout(() => btn.classList.remove('spinning'), 800);
    loadNews(currentIndustry);
}

// ============ 自动刷新 ============
setInterval(() => { if (currentIndustry) loadStocks(currentIndustry); }, 60000);
