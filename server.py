"""
新兴支柱产业追踪系统 - Render云部署版
- 腾讯财经API获取行情
- Google News RSS + 东方财富获取资讯
- 端口使用PORT环境变量
"""
import os
import re
import time
import asyncio
import urllib.request
import json
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


# ============ 产业与代表性股票定义 ============
INDUSTRIES = {
    "ic": {
        "name": "集成电路",
        "subtitle": "Integrated Circuits",
        "icon": "⚡",
        "color": "#0071E3",
        "gradient": "linear-gradient(135deg, #0071E3, #64D2FF)",
        "description": "涵盖芯片设计、制造、封测全产业链",
        "stocks": [
            {"code": "sh688981", "name": "中芯国际", "note": "晶圆代工龙头"},
            {"code": "sz002371", "name": "北方华创", "note": "半导体设备龙头"},
            {"code": "sh603501", "name": "韦尔股份", "note": "芯片设计龙头"},
        ],
        "hk_stocks": [
            {"code": "r_hk00981", "name": "中芯国际"},
        ],
        "news_keywords": ["芯片", "半导体", "集成电路", "晶圆", "EDA", "光刻", "NVIDIA", "GPU"],
        "news_query": "半导体芯片集成电路",
    },
    "biomed": {
        "name": "生物医药",
        "subtitle": "Biomedicine",
        "icon": "🧬",
        "color": "#34C759",
        "gradient": "linear-gradient(135deg, #34C759, #30D158)",
        "description": "创新药、生物制品及CXO产业链",
        "stocks": [
            {"code": "sh603259", "name": "药明康德", "note": "CXO全球龙头"},
            {"code": "sh600276", "name": "恒瑞医药", "note": "创新药龙头"},
            {"code": "sz300760", "name": "迈瑞医疗", "note": "医疗器械龙头"},
        ],
        "hk_stocks": [
            {"code": "r_hk02269", "name": "药明生物"},
        ],
        "news_keywords": ["生物", "医药", "创新药", "临床", "CRO", "疫苗", "FDA", "ADC"],
        "news_query": "生物医药创新药",
    },
    "aerospace": {
        "name": "航空航天",
        "subtitle": "Aerospace",
        "icon": "🚀",
        "color": "#5856D6",
        "gradient": "linear-gradient(135deg, #5856D6, #AF52DE)",
        "description": "民用航空、商业航天与卫星产业",
        "stocks": [
            {"code": "sh600760", "name": "中航沈飞", "note": "军机总装龙头"},
            {"code": "sh600893", "name": "航发动力", "note": "航空发动机龙头"},
            {"code": "sz002179", "name": "中航光电", "note": "军工连接器龙头"},
        ],
        "hk_stocks": [],
        "news_keywords": ["航空", "航天", "大飞机", "C919", "卫星", "火箭", "SpaceX"],
        "news_query": "航空航天C919卫星商业航天",
    },
    "newenergy": {
        "name": "新能源",
        "subtitle": "New Energy",
        "icon": "☀️",
        "color": "#FF9500",
        "gradient": "linear-gradient(135deg, #FF9500, #FFCC00)",
        "description": "光伏、风电、氢能及储能产业链",
        "stocks": [
            {"code": "sz300750", "name": "宁德时代", "note": "动力电池全球龙头"},
            {"code": "sh601012", "name": "隆基绿能", "note": "光伏硅片龙头"},
            {"code": "sz300274", "name": "阳光电源", "note": "光伏逆变器龙头"},
        ],
        "hk_stocks": [
            {"code": "r_hk01799", "name": "新特能源"},
        ],
        "news_keywords": ["光伏", "风电", "储能", "锂电", "氢能", "新能源", "碳中和"],
        "news_query": "新能源光伏风电储能",
    },
    "robot": {
        "name": "具身智能机器人",
        "subtitle": "Embodied AI Robotics",
        "icon": "🤖",
        "color": "#AF52DE",
        "gradient": "linear-gradient(135deg, #AF52DE, #FF6B9D)",
        "description": "人形机器人、核心零部件及系统集成",
        "stocks": [
            {"code": "sz300124", "name": "汇川技术", "note": "伺服系统龙头"},
            {"code": "sh688017", "name": "绿的谐波", "note": "谐波减速器龙头"},
            {"code": "sz300607", "name": "拓斯达", "note": "工业机器人"},
        ],
        "hk_stocks": [],
        "news_keywords": ["机器人", "人形", "具身", "伺服", "减速器", "Optimus"],
        "news_query": "人形机器人具身智能",
    },
    "lowaltitude": {
        "name": "低空经济",
        "subtitle": "Low-Altitude Economy",
        "icon": "🛸",
        "color": "#5AC8FA",
        "gradient": "linear-gradient(135deg, #5AC8FA, #34AADC)",
        "description": "eVTOL、无人机及低空基础设施",
        "stocks": [
            {"code": "sz000099", "name": "中信海直", "note": "通航运营龙头"},
            {"code": "sz002085", "name": "万丰奥威", "note": "eVTOL整机制造"},
            {"code": "sh688070", "name": "纵横股份", "note": "工业无人机"},
        ],
        "hk_stocks": [],
        "news_keywords": ["低空", "eVTOL", "飞行汽车", "通航", "亿航"],
        "news_query": "低空经济eVTOL飞行汽车",
    },
    "newmaterial": {
        "name": "新材料",
        "subtitle": "Advanced Materials",
        "icon": "💎",
        "color": "#FF6B35",
        "gradient": "linear-gradient(135deg, #FF6B35, #FF3B30)",
        "description": "先进复合材料、功能材料及纳米材料",
        "stocks": [
            {"code": "sz002182", "name": "宝武镁业", "note": "镁合金龙头"},
            {"code": "sz300699", "name": "光威复材", "note": "碳纤维龙头"},
            {"code": "sz300777", "name": "中简科技", "note": "高性能碳纤维"},
        ],
        "hk_stocks": [],
        "news_keywords": ["新材料", "碳纤维", "石墨烯", "复合材料", "稀土"],
        "news_query": "新材料碳纤维稀土",
    },
    "quantum": {
        "name": "量子科技",
        "subtitle": "Quantum Technology",
        "icon": "🔮",
        "color": "#5856D6",
        "gradient": "linear-gradient(135deg, #1C1C3D, #5856D6)",
        "description": "量子计算、量子通信及量子精密测量",
        "stocks": [
            {"code": "sh688027", "name": "国盾量子", "note": "量子通信龙头"},
            {"code": "sz300520", "name": "科大国创", "note": "量子计算应用"},
            {"code": "sz000555", "name": "神州信息", "note": "量子保密通信"},
        ],
        "hk_stocks": [],
        "news_keywords": ["量子", "量子计算", "量子通信", "量子比特"],
        "news_query": "量子科技量子计算",
    },
    "6g": {
        "name": "6G通信",
        "subtitle": "6G Communications",
        "icon": "📡",
        "color": "#30B0C7",
        "gradient": "linear-gradient(135deg, #30B0C7, #5AC8FA)",
        "description": "下一代通信技术、太赫兹及通感一体化",
        "stocks": [
            {"code": "sz000063", "name": "中兴通讯", "note": "通信设备龙头"},
            {"code": "sh600498", "name": "烽火通信", "note": "光通信龙头"},
            {"code": "sz300136", "name": "信维通信", "note": "天线射频龙头"},
        ],
        "hk_stocks": [
            {"code": "r_hk00728", "name": "中国电信"},
        ],
        "news_keywords": ["6G", "通信", "太赫兹", "卫星互联网", "5G-A"],
        "news_query": "6G通信太赫兹卫星互联网",
    },
}


# ============ 缓存 ============
class DataCache:
    def __init__(self):
        self._cache: Dict[str, tuple] = {}

    def get(self, key: str, max_age: int = 120) -> Optional[any]:
        if key in self._cache:
            data, ts = self._cache[key]
            if time.time() - ts < max_age:
                return data
            del self._cache[key]
        return None

    def set(self, key: str, data: any):
        self._cache[key] = (data, time.time())

    def clear(self):
        self._cache.clear()

cache = DataCache()


# ============ 腾讯财经API数据获取 ============
def _fetch_qq_quotes(codes: List[str]) -> Dict[str, Dict]:
    if not codes:
        return {}
    cache_key = f"qq_{'_'.join(sorted(codes))}"
    cached = cache.get(cache_key, max_age=120)
    if cached is not None:
        return cached
    codes_str = ",".join(codes)
    url = f"https://qt.gtimg.cn/q={codes_str}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read().decode("gbk", errors="ignore")
    except Exception as e:
        print(f"[ERROR] 腾讯API请求失败: {e}")
        return {}
    result = {}
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        var_part, value_part = line.split("=", 1)
        value_part = value_part.strip('"').strip("'")
        if not value_part:
            continue
        parts = value_part.split("~")
        def safe_float(idx):
            try:
                v = parts[idx] if idx < len(parts) else ""
                return float(v) if v and v not in ("-", "") else None
            except (ValueError, IndexError):
                return None
        def safe_str(idx):
            return parts[idx] if idx < len(parts) else ""
        code_raw = safe_str(2)
        var_name = var_part.strip()
        if var_name.startswith("v_sh"):
            full_code = f"sh{code_raw}"
        elif var_name.startswith("v_sz"):
            full_code = f"sz{code_raw}"
        elif var_name.startswith("v_r_hk") or var_name.startswith("v_hk"):
            full_code = f"r_hk{code_raw}"
        else:
            full_code = code_raw
        price = safe_float(3)
        change_pct = safe_float(32)
        pe_dynamic = safe_float(39)
        pe_ttm = safe_float(52)
        pb = safe_float(46)
        ps = safe_float(56)
        market_cap_yi = safe_float(44)
        result[full_code] = {
            "code": code_raw, "full_code": full_code, "name": safe_str(1),
            "price": price, "change_pct": change_pct,
            "pe": pe_ttm if pe_ttm else pe_dynamic,
            "pb": pb, "ps": ps, "market_cap": market_cap_yi,
            "market_cap_str": f"{market_cap_yi:.0f}亿" if market_cap_yi else "--",
        }
    cache.set(cache_key, result)
    return result


def _fetch_qq_hk_quotes(hk_codes: List[str]) -> Dict[str, Dict]:
    if not hk_codes:
        return {}
    cache_key = f"qq_hk_{'_'.join(sorted(hk_codes))}"
    cached = cache.get(cache_key, max_age=120)
    if cached is not None:
        return cached
    codes_str = ",".join(hk_codes)
    url = f"https://qt.gtimg.cn/q={codes_str}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read().decode("gbk", errors="ignore")
    except Exception as e:
        print(f"[ERROR] 港股API请求失败: {e}")
        return {}
    result = {}
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        var_part, value_part = line.split("=", 1)
        value_part = value_part.strip('"').strip("'")
        if not value_part:
            continue
        parts = value_part.split("~")
        def safe_float(idx):
            try:
                v = parts[idx] if idx < len(parts) else ""
                return float(v) if v and v not in ("-", "") else None
            except (ValueError, IndexError):
                return None
        def safe_str(idx):
            return parts[idx] if idx < len(parts) else ""
        code_raw = safe_str(2)
        full_code = f"r_hk{code_raw}"
        price = safe_float(3)
        change_pct = safe_float(32)
        pe_val = safe_float(62) or safe_float(39)
        ps_val = safe_float(58)
        market_cap_yi = safe_float(44)
        result[full_code] = {
            "code": code_raw, "full_code": full_code, "name": safe_str(1),
            "price": price, "change_pct": change_pct,
            "pe": pe_val, "pb": None, "ps": ps_val, "market_cap": market_cap_yi,
            "market_cap_str": f"{market_cap_yi:.0f}亿HKD" if market_cap_yi else "--",
        }
    cache.set(cache_key, result)
    return result


# ============ 资讯获取（云部署版 - 纯HTTP） ============
def _fetch_news_rss2json(query: str) -> List[Dict]:
    """通过rss2json获取Google News资讯"""
    try:
        rss_url = f"https://news.google.com/rss/search?q={urllib.request.quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.request.quote(rss_url)}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") == "ok" and data.get("items"):
            news_list = []
            for item in data["items"][:5]:
                title = item.get("title", "").strip()
                if not title or len(title) < 8:
                    continue
                source = item.get("author") or item.get("source", "")
                if isinstance(source, dict):
                    source = source.get("title", "")
                pub_date = item.get("pubDate", "")
                try:
                    dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    time_str = pub_date[:16] if pub_date else ""
                desc = re.sub(r'<[^>]+>', '', item.get("description", ""))[:120]
                news_list.append({
                    "title": title[:80], "content": desc,
                    "source": str(source) or "Google News",
                    "time": time_str, "url": item.get("link", ""),
                })
            return news_list
    except Exception as e:
        print(f"[WARN] rss2json failed for {query}: {e}")
    return []


def _fetch_news_eastmoney(keywords: List[str]) -> List[Dict]:
    """备用：东方财富新闻搜索"""
    try:
        keyword = keywords[0] if keywords else ""
        param = json.dumps({
            "uid": "", "keyword": keyword,
            "type": ["cmsArticleWebOld"],
            "client": "web", "clientType": "web", "clientVersion": "curr",
            "param": {"cmsArticleWebOld": {
                "searchScope": "default", "sort": "default",
                "pageIndex": 1, "pageSize": 5, "preTag": "", "postTag": ""
            }}
        }, ensure_ascii=False)
        url = f"https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param={urllib.request.quote(param)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://so.eastmoney.com/"})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read().decode("utf-8", errors="ignore")
        json_str = re.sub(r'^jQuery\(', '', raw).rstrip(')')
        data = json.loads(json_str)
        items = data.get("result", {}).get("cmsArticleWebOld", {}).get("list", [])
        news_list = []
        for item in items[:5]:
            title = re.sub(r'<[^>]+>', '', item.get("title", "")).strip()
            if not title:
                continue
            news_list.append({
                "title": title[:80],
                "content": re.sub(r'<[^>]+>', '', item.get("content", ""))[:120],
                "source": item.get("source", "") or "东方财富",
                "time": item.get("date", "")[:16],
                "url": item.get("url", ""),
            })
        return news_list
    except Exception as e:
        print(f"[WARN] 东方财富新闻 failed: {e}")
    return []


def _fetch_news_sina(keywords: List[str]) -> List[Dict]:
    """备用：新浪7x24关键词匹配"""
    def strip_html(text):
        return re.sub(r'<[^>]+>', '', text).strip()
    all_items = []
    for page in range(1, 3):
        try:
            url = f"https://zhibo.sina.com.cn/api/zhibo/feed?page={page}&page_size=50&zhibo_id=152&tag_id=0&type=0"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("result", {}).get("data", {}).get("feed", {}).get("list", [])
            all_items.extend(items)
        except Exception:
            pass
    news_list = []
    for item in all_items:
        rich = item.get("rich_text", "")
        title = strip_html(rich)[:80]
        content = strip_html(rich)
        if any(kw in title or kw in content for kw in keywords):
            news_list.append({
                "title": title, "content": content[:100],
                "source": "新浪财经7x24",
                "time": item.get("created_at", ""),
                "url": "https://finance.sina.com.cn/7x24/",
            })
    return news_list[:5]


def _fetch_news_sync(industry_name: str, keywords: List[str], search_query: str) -> List[Dict]:
    """获取产业资讯 - 多源级联"""
    cache_key = f"news_{industry_name}"
    cached = cache.get(cache_key, max_age=600)
    if cached is not None:
        return cached
    news_list = _fetch_news_rss2json(search_query)
    if len(news_list) < 3:
        em_news = _fetch_news_eastmoney(keywords)
        existing = {n["title"] for n in news_list}
        for n in em_news:
            if n["title"] not in existing:
                news_list.append(n)
                existing.add(n["title"])
    if len(news_list) < 3:
        sina_news = _fetch_news_sina(keywords)
        existing = {n["title"] for n in news_list}
        for n in sina_news:
            if n["title"] not in existing:
                news_list.append(n)
                existing.add(n["title"])
    cache.set(cache_key, news_list[:5])
    return news_list[:5]


# ============ FastAPI ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.environ.get("PORT", "8765")
    print("=" * 50)
    print("  新兴支柱产业追踪系统")
    print(f"  http://0.0.0.0:{port}")
    print("=" * 50)
    yield

app = FastAPI(title="新兴支柱产业追踪系统", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/industries")
async def get_industries():
    result = []
    for key, ind in INDUSTRIES.items():
        result.append({
            "id": key, "name": ind["name"], "subtitle": ind["subtitle"],
            "icon": ind["icon"], "color": ind["color"], "gradient": ind["gradient"],
            "description": ind["description"],
        })
    return {"industries": result}


@app.get("/api/industry/{industry_id}/stocks")
async def get_industry_stocks(industry_id: str):
    if industry_id not in INDUSTRIES:
        raise HTTPException(status_code=404, detail="产业不存在")
    ind = INDUSTRIES[industry_id]
    a_codes = [s["code"] for s in ind["stocks"]]
    a_quotes = await asyncio.to_thread(_fetch_qq_quotes, a_codes)
    a_stocks = []
    for s in ind["stocks"]:
        q = a_quotes.get(s["code"], {})
        a_stocks.append({
            "code": q.get("code", s["code"][2:]), "name": q.get("name", s["name"]),
            "note": s.get("note", ""), "price": q.get("price"),
            "change_pct": q.get("change_pct"), "pe": q.get("pe"),
            "ps": q.get("ps"), "pb": q.get("pb"),
            "market_cap": q.get("market_cap_str", "--"),
            "market_cap_raw": q.get("market_cap", 0) or 0,
        })
    hk_codes = [s["code"] for s in ind["hk_stocks"]]
    hk_quotes = await asyncio.to_thread(_fetch_qq_hk_quotes, hk_codes) if hk_codes else {}
    hk_stocks = []
    for s in ind["hk_stocks"]:
        q = hk_quotes.get(s["code"], {})
        hk_stocks.append({
            "code": q.get("code", s["code"][2:]), "name": q.get("name", s["name"]),
            "price": q.get("price"), "change_pct": q.get("change_pct"),
            "pe": q.get("pe"), "ps": q.get("ps"), "pb": q.get("pb"),
            "market_cap": q.get("market_cap_str", "--"),
            "market_cap_raw": q.get("market_cap", 0) or 0,
        })
    return {
        "id": industry_id, "name": ind["name"],
        "a_stocks": a_stocks, "hk_stocks": hk_stocks,
        "a_count": len(a_stocks), "hk_count": len(hk_stocks),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/industry/{industry_id}/news")
async def get_industry_news(industry_id: str):
    if industry_id not in INDUSTRIES:
        raise HTTPException(status_code=404, detail="产业不存在")
    ind = INDUSTRIES[industry_id]
    news = await asyncio.to_thread(_fetch_news_sync, ind["name"], ind["news_keywords"], ind["search_query"])
    return {"id": industry_id, "name": ind["name"], "news": news, "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


@app.post("/api/cache/clear")
async def clear_cache():
    cache.clear()
    return {"status": "ok", "message": "缓存已清除"}


# ============ 静态文件 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run(app, host="0.0.0.0", port=port)
