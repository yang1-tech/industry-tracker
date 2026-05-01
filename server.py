"""
新兴支柱产业追踪系统 - 后端服务 (腾讯财经API版)
每个产业展示3只代表性股票 + 实时行情
"""
import os
import re
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import subprocess
import json

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
        "news_keywords": ["芯片", "半导体", "集成电路", "晶圆", "EDA", "光刻", "中芯", "华创", "封测", "存储", "GPU", "NVIDIA"],
        "search_query": "半导体芯片集成电路新闻",
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
        "news_keywords": ["生物", "医药", "创新药", "临床", "CRO", "疫苗", "药明", "恒瑞", "迈瑞", "FDA", "GLP", "ADC", "基因"],
        "search_query": "生物医药创新药新闻",
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
        "news_keywords": ["航空", "航天", "大飞机", "C919", "卫星", "火箭", "商飞", "航发", "军工", "无人机", "SpaceX"],
        "search_query": "航空航天C919卫星商业航天新闻",
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
        "news_keywords": ["光伏", "风电", "储能", "锂电", "氢能", "新能源", "宁德", "隆基", "电池", "充电桩", "碳中和"],
        "search_query": "新能源光伏风电核电储能新闻",
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
        "news_keywords": ["机器人", "人形", "具身", "伺服", "减速器", "自动化", "工业母机", "智能制造", "Optimus"],
        "search_query": "人形机器人具身智能新闻",
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
        "news_keywords": ["低空", "eVTOL", "飞行汽车", "通航", "小鹏", "亿航", "空域", "低空经济"],
        "search_query": "低空经济eVTOL新闻",
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
        "news_keywords": ["新材料", "碳纤维", "石墨烯", "复合材料", "镁合金", "钛合金", "稀土", "纳米", "芳纶"],
        "search_query": "新材料碳纤维稀土新闻",
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
        "news_keywords": ["量子", "量子计算", "量子通信", "国盾", "量子加密", "量子芯片", "量子比特"],
        "search_query": "量子科技量子计算新闻",
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
        "news_keywords": ["6G", "通信", "太赫兹", "通感", "卫星互联网", "中兴", "烽火", "光通信", "5G-A", "物联网"],
        "search_query": "6G通信太赫兹卫星互联网新闻",
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
    """批量获取腾讯财经实时行情"""
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

        # 解析字段
        def safe_float(idx):
            try:
                v = parts[idx] if idx < len(parts) else ""
                return float(v) if v and v not in ("-", "") else None
            except (ValueError, IndexError):
                return None

        def safe_str(idx):
            return parts[idx] if idx < len(parts) else ""

        code_raw = safe_str(2)  # 纯数字代码
        # 构建完整代码（加市场前缀）
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
        pre_close = safe_float(4)
        change_pct = safe_float(32)
        change_amt = safe_float(31)
        pe_dynamic = safe_float(39)
        pe_ttm = safe_float(52)
        pb = safe_float(46)
        ps = safe_float(56)
        market_cap_yi = safe_float(44)  # 亿元
        turnover_rate = safe_float(38)

        result[full_code] = {
            "code": code_raw,
            "full_code": full_code,
            "name": safe_str(1),
            "price": price,
            "pre_close": pre_close,
            "change_pct": change_pct,
            "change_amt": change_amt,
            "pe": pe_ttm if pe_ttm else pe_dynamic,
            "pb": pb,
            "ps": ps,
            "market_cap": market_cap_yi,
            "market_cap_str": f"{market_cap_yi:.0f}亿" if market_cap_yi else "--",
            "turnover_rate": turnover_rate,
        }

    cache.set(cache_key, result)
    return result


def _fetch_qq_hk_quotes(hk_codes: List[str]) -> Dict[str, Dict]:
    """获取港股行情（腾讯财经）"""
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

        var_name = var_part.strip()
        code_raw = safe_str(2)
        full_code = f"r_hk{code_raw}"

        price = safe_float(3)
        pre_close = safe_float(4)
        change_pct = safe_float(32)
        change_amt = safe_float(31)
        pe_val = safe_float(62) or safe_float(39)  # [62]=PE_TTM, [39]=PE(dynamic)
        ps_val = safe_float(58)  # [58]=PS
        market_cap_yi = safe_float(44)  # 亿港元

        result[full_code] = {
            "code": code_raw,
            "full_code": full_code,
            "name": safe_str(1),
            "price": price,
            "pre_close": pre_close,
            "change_pct": change_pct,
            "change_amt": change_amt,
            "pe": pe_val,
            "pb": None,
            "ps": ps_val,
            "market_cap": market_cap_yi,
            "market_cap_str": f"{market_cap_yi:.0f}亿HKD" if market_cap_yi else "--",
            "turnover_rate": safe_float(38),
        }

    cache.set(cache_key, result)
    return result


# ============ 资讯获取 ============
import re as _re

# ProSearch脚本路径
_NODE_BIN = r"C:\Program Files\QClaw\resources\node\node.exe"
_PROSEARCH_SCRIPT = os.path.join(
    os.environ.get('ProgramFiles', r'C:\Program Files'),
    'QClaw', 'resources', 'openclaw', 'config', 'skills',
    'online-search', 'scripts', 'prosearch.cjs'
)

# 创建中文关键词传递的Node wrapper（解决Windows GBK编码问题）
import tempfile as _tempfile
_WRAPPER_JS = """const { execFileSync } = require('child_process');
const keyword = process.env.PROSEARCH_KEYWORD;
const freshness = process.env.PROSEARCH_FRESHNESS || '7d';
const industry = process.env.PROSEARCH_INDUSTRY || 'news';
const scriptPath = process.argv[2];
const args = [scriptPath, '--keyword=' + keyword, '--freshness=' + freshness, '--industry=' + industry];
try { const result = execFileSync(process.execPath, args, { encoding: 'utf-8', timeout: 15000 }); process.stdout.write(result); } catch(e) { process.stdout.write(JSON.stringify({success:false, message: e.message})); }
"""
_WRAPPER_PATH = os.path.join(_tempfile.gettempdir(), "_prosearch_wrapper.cjs")
with open(_WRAPPER_PATH, 'w', encoding='utf-8') as _f:
    _f.write(_WRAPPER_JS)

def _fetch_news_prosearch(query: str) -> List[Dict]:
    """通过ProSearch获取产业专属新闻（用环境变量传递中文关键词避免GBK编码问题）"""
    try:
        env = os.environ.copy()
        env["PROSEARCH_KEYWORD"] = query
        env["PROSEARCH_FRESHNESS"] = "7d"
        env["PROSEARCH_INDUSTRY"] = "news"

        result = subprocess.run(
            [_NODE_BIN, _WRAPPER_PATH, _PROSEARCH_SCRIPT],
            capture_output=True, timeout=20,
            env=env
        )
        stdout = result.stdout.decode('utf-8', errors='replace')

        if not stdout.strip():
            print(f"[WARN] ProSearch empty stdout for: {query}")
            return []

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as e:
            print(f"[WARN] ProSearch JSON parse error for {query}: {e}")
            return []

        if not data.get("success", False):
            print(f"[WARN] ProSearch failed for {query}: {data.get('message','')[:100]}")
            return []

        docs = data.get("data", {}).get("docs", [])
        news_list = []
        for doc in docs:
            title = doc.get("title", "").strip()
            passage = doc.get("passage", "").strip()
            url = doc.get("url", "")
            date = doc.get("date", "")
            site = doc.get("site", "")
            # 过滤掉股票行情页和无关内容
            if not title or '行情走势' in title or '行情_' in title:
                continue
            if len(title) < 8:
                continue
            news_list.append({
                "title": title[:80],
                "content": passage[:120],
                "source": site or "腾讯元宝搜索",
                "time": date[:16] if date else "",
                "url": url,
            })
        return news_list[:5]
    except subprocess.TimeoutExpired:
        print(f"[WARN] ProSearch timeout for: {query}")
        return []
    except Exception as e:
        print(f"[WARN] ProSearch error for {query}: {e}")
        return []


def _fetch_news_sina(keywords: List[str]) -> List[Dict]:
    """备用：新浪7x24关键词匹配"""
    import re as _re2
    def strip_html(text):
        return _re2.sub(r'<[^>]+>', '', text).strip()

    all_items = []
    for page in range(1, 3):
        try:
            url = f"https://zhibo.sina.com.cn/api/zhibo/feed?page={page}&page_size=50&zhibo_id=152&tag_id=0&type=0"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.sina.com.cn/"
            })
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
                "title": title,
                "content": content[:100],
                "source": "新浪财经7x24",
                "time": item.get("created_at", ""),
                "url": "https://finance.sina.com.cn/7x24/",
            })
    return news_list[:5]


def _fetch_news_sync(industry_name: str, keywords: List[str], search_query: str) -> List[Dict]:
    """获取产业资讯 - 优先ProSearch，备用新浪7x24"""
    cache_key = f"news_{industry_name}"
    cached = cache.get(cache_key, max_age=600)
    if cached is not None:
        return cached

    # 优先使用ProSearch
    news_list = _fetch_news_prosearch(search_query)

    # 如果ProSearch结果不足，用新浪7x24补充
    if len(news_list) < 3:
        sina_news = _fetch_news_sina(keywords)
        # 去重
        existing_titles = {n["title"] for n in news_list}
        for n in sina_news:
            if n["title"] not in existing_titles:
                news_list.append(n)
                existing_titles.add(n["title"])

    cache.set(cache_key, news_list[:5])
    return news_list[:5]


# ============ FastAPI ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("  新兴支柱产业追踪系统")
    print("  http://localhost:8765")
    print("=" * 50)
    yield

app = FastAPI(title="新兴支柱产业追踪系统", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/industries")
async def get_industries():
    result = []
    for key, ind in INDUSTRIES.items():
        result.append({
            "id": key,
            "name": ind["name"],
            "subtitle": ind["subtitle"],
            "icon": ind["icon"],
            "color": ind["color"],
            "gradient": ind["gradient"],
            "description": ind["description"],
        })
    return {"industries": result}


@app.get("/api/industry/{industry_id}/stocks")
async def get_industry_stocks(industry_id: str):
    if industry_id not in INDUSTRIES:
        raise HTTPException(status_code=404, detail="产业不存在")

    ind = INDUSTRIES[industry_id]

    # 获取A股行情
    a_codes = [s["code"] for s in ind["stocks"]]
    a_quotes = await asyncio.to_thread(_fetch_qq_quotes, a_codes)

    a_stocks = []
    for s in ind["stocks"]:
        q = a_quotes.get(s["code"], {})
        a_stocks.append({
            "code": q.get("code", s["code"][2:]),
            "name": q.get("name", s["name"]),
            "note": s.get("note", ""),
            "price": q.get("price"),
            "change_pct": q.get("change_pct"),
            "pe": q.get("pe"),
            "ps": q.get("ps"),
            "pb": q.get("pb"),
            "market_cap": q.get("market_cap_str", "--"),
            "market_cap_raw": q.get("market_cap", 0) or 0,
        })

    # 获取港股行情
    hk_codes = [s["code"] for s in ind["hk_stocks"]]
    hk_quotes = await asyncio.to_thread(_fetch_qq_hk_quotes, hk_codes) if hk_codes else {}

    hk_stocks = []
    for s in ind["hk_stocks"]:
        q = hk_quotes.get(s["code"], {})
        hk_stocks.append({
            "code": q.get("code", s["code"][2:]),
            "name": q.get("name", s["name"]),
            "price": q.get("price"),
            "change_pct": q.get("change_pct"),
            "pe": q.get("pe"),
            "ps": q.get("ps"),
            "pb": q.get("pb"),
            "market_cap": q.get("market_cap_str", "--"),
            "market_cap_raw": q.get("market_cap", 0) or 0,
        })

    return {
        "id": industry_id,
        "name": ind["name"],
        "a_stocks": a_stocks,
        "hk_stocks": hk_stocks,
        "a_count": len(a_stocks),
        "hk_count": len(hk_stocks),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/industry/{industry_id}/news")
async def get_industry_news(industry_id: str):
    if industry_id not in INDUSTRIES:
        raise HTTPException(status_code=404, detail="产业不存在")

    ind = INDUSTRIES[industry_id]
    news = await asyncio.to_thread(_fetch_news_sync, ind["name"], ind["news_keywords"], ind["search_query"])
    return {
        "id": industry_id,
        "name": ind["name"],
        "news": news,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


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
    uvicorn.run(app, host="0.0.0.0", port=8765)
