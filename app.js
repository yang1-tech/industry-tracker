/**
 * 新兴支柱产业追踪 - 纯前端版
 * 股票：腾讯财经 JSONP
 * 新闻：rss2json.com + allorigins 备用
 */

// ============ 产业配置 ============
const INDUSTRIES = {
    ic: {
        name: '集成电路', subtitle: 'Integrated Circuits', icon: '⚡',
        color: '#0071E3', gradient: 'linear-gradient(135deg, #0071E3, #64D2FF)',
        description: '涵盖芯片设计、制造、封测全产业链',
        stocks: [
            { code: 'sh688981', name: '中芯国际', note: '晶圆代工龙头' },
            { code: 'sz002371', name: '北方华创', note: '半导体设备龙头' },
            { code: 'sh603501', name: '韦尔股份', note: '芯片设计龙头' },
        ],
        hk_stocks: [{ code: 'r_hk00981', name: '中芯国际' }],
        newsQuery: '半导体芯片集成电路',
    },
    biomed: {
        name: '生物医药', subtitle: 'Biomedicine', icon: '🧬',
        color: '#34C759', gradient: 'linear-gradient(135deg, #34C759, #30D158)',
        description: '创新药、生物制品及CXO产业链',
        stocks: [
            { code: 'sh603259', name: '药明康德', note: 'CXO全球龙头' },
            { code: 'sh600276', name: '恒瑞医药', note: '创新药龙头' },
            { code: 'sz300760', name: '迈瑞医疗', note: '医疗器械龙头' },
        ],
        hk_stocks: [{ code: 'r_hk02269', name: '药明生物' }],
        newsQuery: '生物医药创新药',
    },
    aerospace: {
        name: '航空航天', subtitle: 'Aerospace', icon: '🚀',
        color: '#5856D6', gradient: 'linear-gradient(135deg, #5856D6, #AF52DE)',
        description: '民用航空、商业航天与卫星产业',
        stocks: [
            { code: 'sh600760', name: '中航沈飞', note: '军机总装龙头' },
            { code: 'sh600893', name: '航发动力', note: '航空发动机龙头' },
            { code: 'sz002179', name: '中航光电', note: '军工连接器龙头' },
        ],
        hk_stocks: [],
        newsQuery: '航空航天C919商业航天',
    },
    newenergy: {
        name: '新能源', subtitle: 'New Energy', icon: '☀️',
        color: '#FF9500', gradient: 'linear-gradient(135deg, #FF9500, #FFCC00)',
        description: '光伏、风电、氢能及储能产业链',
        stocks: [
            { code: 'sz300750', name: '宁德时代', note: '动力电池全球龙头' },
            { code: 'sh601012', name: '隆基绿能', note: '光伏硅片龙头' },
            { code: 'sz300274', name: '阳光电源', note: '光伏逆变器龙头' },
        ],
        hk_stocks: [{ code: 'r_hk01799', name: '新特能源' }],
        newsQuery: '新能源光伏风电储能',
    },
    robot: {
        name: '具身智能机器人', subtitle: 'Embodied AI Robotics', icon: '🤖',
        color: '#AF52DE', gradient: 'linear-gradient(135deg, #AF52DE, #FF6B9D)',
        description: '人形机器人、核心零部件及系统集成',
        stocks: [
            { code: 'sz300124', name: '汇川技术', note: '伺服系统龙头' },
            { code: 'sh688017', name: '绿的谐波', note: '谐波减速器龙头' },
            { code: 'sz300607', name: '拓斯达', note: '工业机器人' },
        ],
        hk_stocks: [],
        newsQuery: '人形机器人具身智能',
    },
    lowaltitude: {
        name: '低空经济', subtitle: 'Low-Altitude Economy', icon: '🛸',
        color: '#5AC8FA', gradient: 'linear-gradient(135deg, #5AC8FA, #34AADC)',
        description: 'eVTOL、无人机及低空基础设施',
        stocks: [
            { code: 'sz000099', name: '中信海直', note: '通航运营龙头' },
            { code: 'sz002085', name: '万丰奥威', note: 'eVTOL整机制造' },
            { code: 'sh688070', name: '纵横股份', note: '工业无人机' },
        ],
        hk_stocks: [],
        newsQuery: '低空经济eVTOL飞行汽车',
    },
    newmaterial: {
        name: '新材料', subtitle: 'Advanced Materials', icon: '💎',
        color: '#FF6B35', gradient: 'linear-gradient(135deg, #FF6B35, #FF3B30)',
        description: '先进复合材料、功能材料及纳米材料',
        stocks: [
            { code: 'sz002182', name: '宝武镁业', note: '镁合金龙头' },
            { code: 'sz300699', name: '光威复材', note: '碳纤维龙头' },
            { code: 'sz300777', name: '中简科技', note: '高性能碳纤维' },
        ],
        hk_stocks: [],
        newsQuery: '新材料碳纤维稀土',
    },
    quantum: {
        name: '量子科技', subtitle: 'Quantum Technology', icon: '🔮',
        color: '#5856D6', gradient: 'linear-gradient(135deg, #1C1C3D, #5856D6)',
        description: '量子计算、量子通信及量子精密测量',
        stocks: [
            { code: 'sh688027', name: '国盾量子', note: '量子通信龙头' },
            { code: 'sz300520', name: '科大国创', note: '量子计算应用' },
            { code: 'sz000555', name: '神州信息', note: '量子保密通信' },
        ],
        hk_stocks: [],
        newsQuery: '量子科技量子计算',
    },
    '6g': {
        name: '6G通信', subtitle: '6G Communications', icon: '📡',
        color: '#30B0C7', gradient: 'linear-gradient(135deg, #30B0C7, #5AC8FA)',
        description: '下一代通信技术、太赫兹及通感一体化',
        stocks: [
            { code: 'sz000063', name: '中兴通讯', note: '通信设备龙头' },
            { code: 'sh600498', name: '烽火通信', note: '光通信龙头' },
            { code: 'sz300136', name: '信维通信', note: '天线射频龙头' },
        ],
        hk_stocks: [{ code: 'r_hk00728', name: '中国电信' }],
        newsQuery: '6G通信太赫兹卫星互联网',
    },
};

// ============ 缓存 ============
const stockCache = {};   // { code: { data, timestamp } }
const newsCache = {};    // { industryId: { data, timestamp } }
const CACHE_STOCK_MS = 60_000;
const CACHE_NEWS_MS = 600_000;

// ============ 腾讯财经 JSONP ============
function fetchStockData(codes) {
    const now = Date.now();
    const uncached = codes.filter(c => !stockCache[c] || now - stockCache[c].timestamp > CACHE_STOCK_MS);

    if (uncached.length === 0) {
        return Promise.resolve(codes.map(c => stockCache[c].data).filter(Boolean));
    }

    // Clean previous globals
    uncached.forEach(c => { delete window[`v_${c}`]; });

    return new Promise(resolve => {
        const script = document.createElement('script');
        script.charset = 'gbk';
        script.src = `https://qt.gtimg.cn/q=${uncached.join(',')}`;

        const timeout = setTimeout(() => {
            cleanup();
            resolve(codes.map(c => stockCache[c]?.data).filter(Boolean));
        }, 8000);

        script.onload = () => {
            clearTimeout(timeout);
            uncached.forEach(code => {
                const key = `v_${code}`;
                if (window[key] && window[key] !== '') {
                    const parsed = parseQQQuote(window[key], code);
                    stockCache[code] = { data: parsed, timestamp: now };
                }
                delete window[key];
            });
            cleanup();
            resolve(codes.map(c => stockCache[c]?.data).filter(Boolean));
        };

        script.onerror = () => {
            clearTimeout(timeout);
            cleanup();
            resolve(codes.map(c => stockCache[c]?.data).filter(Boolean));
        };

        function cleanup() {
            if (script.parentNode) script.parentNode.removeChild(script);
        }

        document.head.appendChild(script);
    });
}

function parseQQQuote(raw, code) {
    const p = raw.split('~');
    const sf = i => { const v = p[i]; return (v && v !== '-') ? parseFloat(v) : null; };
    const ss = i => (i < p.length) ? p[i] : '';
    const isHK = code.startsWith('r_hk');

    const price = sf(3);
    const change_pct = sf(32);
    const pe_ttm = sf(52);
    const pe_dyn = sf(39);
    const ps = isHK ? (sf(58) || sf(56)) : sf(56);
    const pb = sf(46);
    const cap = sf(44);

    return {
        code: ss(2), fullCode: code, name: ss(1),
        price, change_pct,
        pe: pe_ttm || pe_dyn,
        ps, pb,
        marketCap: cap,
        marketCapStr: formatCap(cap, isHK),
        isHK,
    };
}

function formatCap(val, isHK) {
    if (!val) return '--';
    if (val >= 10000) return (val / 10000).toFixed(2) + '万亿';
    if (val >= 100) return val.toFixed(0) + '亿';
    return val.toFixed(1) + '亿';
}

// ============ 新闻获取 ============
async function fetchNews(industryId) {
    const now = Date.now();
    if (newsCache[industryId] && now - newsCache[industryId].timestamp < CACHE_NEWS_MS) {
        return newsCache[industryId].data;
    }

    const ind = INDUSTRIES[industryId];
    if (!ind) return [];

    let news = [];

    // Primary: rss2json
    try {
        const rssUrl = `https://news.google.com/rss/search?q=${encodeURIComponent(ind.newsQuery)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans`;
        const apiUrl = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssUrl)}`;
        const resp = await fetch(apiUrl, { signal: AbortSignal.timeout(8000) });
        const data = await resp.json();
        if (data.status === 'ok' && data.items?.length) {
            news = data.items.slice(0, 6).map(item => {
                const desc = (item.description || '').replace(/<[^>]+>/g, '').slice(0, 120);
                let timeStr = '';
                if (item.pubDate) {
                    try { timeStr = new Date(item.pubDate).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch {}
                }
                return {
                    title: (item.title || '').slice(0, 80),
                    content: desc, source: item.author || 'Google News',
                    time: timeStr, url: item.link || '',
                };
            }).filter(n => n.title && n.title.length > 5);
        }
    } catch (e) { console.warn('rss2json failed:', e); }

    // Fallback: allorigins + XML parsing
    if (news.length < 3) {
        try {
            const rssUrl = `https://news.google.com/rss/search?q=${encodeURIComponent(ind.newsQuery)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans`;
            const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(rssUrl)}`;
            const resp = await fetch(proxyUrl, { signal: AbortSignal.timeout(8000) });
            const text = await resp.text();
            const xml = new DOMParser().parseFromString(text, 'text/xml');
            const items = xml.querySelectorAll('item');
            const existing = new Set(news.map(n => n.title));
            Array.from(items).slice(0, 8).forEach(item => {
                const title = item.querySelector('title')?.textContent || '';
                if (title.length <= 5 || existing.has(title)) return;
                let timeStr = '';
                const pubDate = item.querySelector('pubDate')?.textContent;
                if (pubDate) {
                    try { timeStr = new Date(pubDate).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch {}
                }
                news.push({
                    title: title.slice(0, 80), content: '',
                    source: item.querySelector('source')?.textContent || 'Google News',
                    time: timeStr,
                    url: item.querySelector('link')?.textContent || '',
                });
                existing.add(title);
            });
        } catch (e) { console.warn('allorigins fallback failed:', e); }
    }

    news = news.slice(0, 5);
    newsCache[industryId] = { data: news, timestamp: now };
    return news;
}

// ============ 路由 ============
function getRoute() {
    const hash = location.hash.slice(1);
    return hash || '';
}

function navigate(hash) {
    location.hash = hash;
}

window.addEventListener('hashchange', render);

// ============ 渲染 ============
async function render() {
    const route = getRoute();
    const app = document.getElementById('app');

    if (route && INDUSTRIES[route]) {
        await renderDetail(app, route);
    } else {
        await renderHome(app);
    }
}

async function renderHome(app) {
    const industryKeys = Object.keys(INDUSTRIES);

    app.innerHTML = `
        <div class="header">
            <h1>新兴支柱产业追踪</h1>
            <div class="subtitle">EMERGING PILLAR INDUSTRY TRACKER</div>
            <div class="update-info">
                <span class="update-dot"></span>
                数据来源：腾讯财经 · 实时更新
            </div>
        </div>
        <div class="grid" id="grid">
            ${industryKeys.map(key => {
                const ind = INDUSTRIES[key];
                return `
                    <div class="industry-card" data-id="${key}" style="--card-gradient: ${ind.gradient}">
                        <span class="card-icon">${ind.icon}</span>
                        <div class="card-name">${ind.name}</div>
                        <div class="card-subtitle">${ind.subtitle}</div>
                        <div class="card-desc">${ind.description}</div>
                        <div class="card-arrow">
                            <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        <div class="footer">
            数据来源 <a href="https://gu.qq.com" target="_blank">腾讯财经</a> · 
            新闻来源 <a href="https://news.google.com" target="_blank">Google News</a> · 
            自动刷新中
        </div>
    `;

    // Bind click events
    app.querySelectorAll('.industry-card').forEach(card => {
        card.addEventListener('click', () => navigate(card.dataset.id));
    });

    // Prefetch stock data in background
    setTimeout(() => prefetchAllStocks(), 500);
}

async function prefetchAllStocks() {
    for (const key of Object.keys(INDUSTRIES)) {
        const ind = INDUSTRIES[key];
        const codes = [...ind.stocks.map(s => s.code), ...ind.hk_stocks.map(s => s.code)];
        await fetchStockData(codes).catch(() => {});
        await new Promise(r => setTimeout(r, 300)); // rate limit
    }
}

async function renderDetail(app, industryId) {
    const ind = INDUSTRIES[industryId];

    app.innerHTML = `
        <div class="detail-view">
            <div class="detail-header">
                <button class="back-btn" id="backBtn">
                    <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
                    返回
                </button>
                <div class="detail-title">
                    <h2>${ind.icon} ${ind.name}</h2>
                    <div class="desc">${ind.description}</div>
                </div>
            </div>
            <div class="section">
                <div class="section-title">📊 代表性公司</div>
                <div id="stocksContainer">
                    <div class="loading-spinner"><div class="spinner"></div> 加载行情中...</div>
                </div>
            </div>
            <div class="section">
                <div class="section-title">📰 最新资讯</div>
                <div id="newsContainer">
                    <div class="loading-spinner"><div class="spinner"></div> 加载资讯中...</div>
                </div>
            </div>
        </div>
    `;

    document.getElementById('backBtn').addEventListener('click', () => navigate(''));

    // Fetch stocks
    try {
        const aCodes = ind.stocks.map(s => s.code);
        const hkCodes = ind.hk_stocks.map(s => s.code);
        const allCodes = [...aCodes, ...hkCodes];
        const quotes = await fetchStockData(allCodes);
        const quoteMap = {};
        quotes.forEach(q => { quoteMap[q.fullCode] = q; });

        const stocksHtml = `
            <div class="stock-table">
                <div class="stock-row header">
                    <div>公司</div>
                    <div>现价</div>
                    <div>涨跌幅</div>
                    <div class="stock-pe" style="text-align:right">PE</div>
                    <div class="stock-ps" style="text-align:right">PS</div>
                    <div class="stock-cap" style="text-align:right">市值</div>
                </div>
                ${ind.stocks.map(s => {
                    const q = quoteMap[s.code] || {};
                    const changeClass = (q.change_pct > 0) ? 'up' : (q.change_pct < 0) ? 'down' : 'flat';
                    const changeStr = q.change_pct != null ? (q.change_pct > 0 ? '+' : '') + q.change_pct.toFixed(2) + '%' : '--';
                    return `
                        <div class="stock-row">
                            <div>
                                <span class="stock-name">${q.name || s.name}<span class="note">${s.note || ''}</span></span>
                                <span class="stock-label a-share">A股</span>
                                <div class="stock-code">${q.code || s.code.slice(2)}</div>
                            </div>
                            <div class="stock-price ${changeClass}">${q.price != null ? q.price.toFixed(2) : '--'}</div>
                            <div class="stock-change ${changeClass}">${changeStr}</div>
                            <div class="stock-pe">${q.pe != null ? q.pe.toFixed(1) : '--'}</div>
                            <div class="stock-ps">${q.ps != null ? q.ps.toFixed(1) : '--'}</div>
                            <div class="stock-cap">${q.marketCapStr || '--'}</div>
                        </div>
                    `;
                }).join('')}
                ${ind.hk_stocks.map(s => {
                    const q = quoteMap[s.code] || {};
                    const changeClass = (q.change_pct > 0) ? 'up' : (q.change_pct < 0) ? 'down' : 'flat';
                    const changeStr = q.change_pct != null ? (q.change_pct > 0 ? '+' : '') + q.change_pct.toFixed(2) + '%' : '--';
                    return `
                        <div class="stock-row">
                            <div>
                                <span class="stock-name">${q.name || s.name}</span>
                                <span class="stock-label hk">港股</span>
                                <div class="stock-code">${q.code || s.code.slice(2)}</div>
                            </div>
                            <div class="stock-price ${changeClass}">${q.price != null ? q.price.toFixed(2) : '--'}</div>
                            <div class="stock-change ${changeClass}">${changeStr}</div>
                            <div class="stock-pe">${q.pe != null ? q.pe.toFixed(1) : '--'}</div>
                            <div class="stock-ps">${q.ps != null ? q.ps.toFixed(1) : '--'}</div>
                            <div class="stock-cap">${q.marketCapStr || '--'}</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        document.getElementById('stocksContainer').innerHTML = stocksHtml;
    } catch (e) {
        document.getElementById('stocksContainer').innerHTML = `
            <div class="error-state">
                行情数据加载失败
                <button class="retry-btn" onclick="location.reload()">重试</button>
            </div>
        `;
    }

    // Fetch news
    try {
        const news = await fetchNews(industryId);
        if (news.length === 0) {
            document.getElementById('newsContainer').innerHTML = `
                <div class="news-empty">暂无相关资讯，请稍后再试</div>
            `;
        } else {
            document.getElementById('newsContainer').innerHTML = `
                <div class="news-list">
                    ${news.map(n => `
                        <a class="news-item" href="${n.url}" target="_blank" rel="noopener">
                            <div class="news-title">${n.title}</div>
                            <div class="news-meta">
                                <span class="news-source">${n.source}</span>
                                <span>${n.time}</span>
                            </div>
                        </a>
                    `).join('')}
                </div>
            `;
        }
    } catch (e) {
        document.getElementById('newsContainer').innerHTML = `
            <div class="news-empty">资讯加载失败</div>
        `;
    }
}

// ============ 自动刷新 ============
let refreshTimer = null;

function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => {
        const route = getRoute();
        if (route && INDUSTRIES[route]) {
            // Clear stock cache for current industry to force refresh
            const ind = INDUSTRIES[route];
            [...ind.stocks, ...ind.hk_stocks].forEach(s => { delete stockCache[s.code]; });
            render();
        }
    }, 60_000);
}

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', () => {
    render();
    startAutoRefresh();
});
