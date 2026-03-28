"""
Academic AI Tools News Collector
专门采集学术研究/论文写作相关的 AI 工具新闻
数据源：Product Hunt (Atom) + HN Show HN + GitHub
筛选原则：只保留工具/软件/平台，过滤掉纯论文/新闻
"""

import json
import os
import re
import html
from datetime import datetime

try:
    import httpx
    def http_get_text(url, headers=None, timeout=20):
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers or {})
            resp.raise_for_status()
            return resp.text
    def http_get_json(url, headers=None, timeout=20):
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers or {})
            resp.raise_for_status()
            return resp.json()
except ImportError:
    import urllib.request, urllib.parse
    def http_get_text(url, headers=None, timeout=20):
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    def http_get_json(url, headers=None, timeout=20):
        return json.loads(http_get_text(url, headers, timeout))


# ============================================================
# 关键词定义
# ============================================================

# 必须命中：工具/平台相关词
TOOL_KEYWORDS = [
    'tool', 'platform', 'app', 'software', 'plugin', 'extension', 'api',
    'assistant', 'agent', 'workflow', 'automation', 'search', 'reader',
    'writer', 'editor', 'generator', 'analyzer', 'detector', 'tracker',
    'manager', 'organizer', 'dashboard', 'library', 'framework',
    'citation', 'reference', 'bibliography', 'zotero', 'mendeley',
    'latex', 'overleaf', 'grammarly', 'turnitin', 'plagiarism',
    'summarize', 'summarizer', 'summary', 'abstract', 'review',
    'literature', 'scholarly', 'academic', 'research', 'paper',
    'writing', 'editing', 'proofreading', 'translation', 'pdf',
    'note', 'notes', 'notetaking', 'knowledge base', 'rag', 'retrieval',
    'semantic search', 'embedding', 'chatbot', 'copilot', 'autocomplete',
]

# 排除词：如果 title 里有这些词，不是工具（可能是论文/公司/事件）
EXCLUDE_KEYWORDS = [
    'autonomous driving', 'self-driving', 'robotics', 'robot', 'drone',
    'cryptocurrency', 'blockchain', 'nft', 'defi', 'trading',
    'medical', 'clinical', 'hospital', 'patient', 'drug', 'cancer',
    'survey', 'framework for', 'approach to', 'method for',
    'towards', 'learning to', 'revisiting', 'rethinking',
    'a novel', 'a new approach', 'benchmark',
]

# 强相关：命中这些词的直接纳入（高优先级）
HIGH_PRIORITY_KEYWORDS = [
    'zotero', 'mendeley', 'endnote', 'overleaf', 'latex',
    'research assistant', 'literature review', 'citation manager',
    'paper writing', 'academic writing', 'thesis', 'dissertation',
    'reference manager', 'pdf reader', 'semantic scholar',
    'connected papers', 'research rabbit', 'elicit', 'consensus',
    'scite', 'litmaps', 'inciteful',
]


def is_research_tool(title, description=""):
    """判断是否是学术研究相关工具"""
    text = (title + " " + description).lower()
    
    # 高优先级：直接通过
    if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
        return True, 3  # score=3
    
    # 排除词：直接过滤
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False, 0
    
    # 工具词命中数
    tool_score = sum(1 for kw in TOOL_KEYWORDS if kw in text)
    
    # 必须同时有"研究/学术"语境 AND "工具"语境
    research_context = any(kw in text for kw in [
        'research', 'academic', 'scholar', 'paper', 'literature',
        'writing', 'citation', 'pdf', 'thesis', 'journal', 'review'
    ])
    
    if research_context and tool_score >= 2:
        return True, tool_score
    
    return False, 0


# ============================================================
# 数据源 1：Product Hunt（Atom RSS）
# ============================================================

def fetch_product_hunt():
    """从 Product Hunt RSS 获取最新工具"""
    results = []
    try:
        xml = http_get_text(
            "https://www.producthunt.com/feed",
            headers={"User-Agent": "Mozilla/5.0 (compatible; AcademicRadar/1.0)"}
        )
        
        entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
        
        for entry in entries:
            title_m = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            content_m = re.search(r'<content[^>]*>(.*?)</content>', entry, re.DOTALL)
            link_m = re.search(r'<link[^/].*?href="(.*?)"', entry)
            date_m = re.search(r'<published>(.*?)</published>', entry)
            
            title = html.unescape(title_m.group(1).strip()) if title_m else ""
            content_raw = content_m.group(1) if content_m else ""
            desc = html.unescape(re.sub(r'&lt;.*?&gt;|<.*?>', '', content_raw)).strip()[:300]
            url = link_m.group(1) if link_m else ""
            date_str = date_m.group(1)[:10] if date_m else ""
            
            if not title or not url:
                continue
            
            ok, score = is_research_tool(title, desc)
            if ok:
                results.append({
                    "title": title,
                    "summary": desc[:200] if desc else f"New tool on Product Hunt: {title}",
                    "url": url,
                    "source": "Product Hunt",
                    "icon": "🚀",
                    "date": date_str,
                    "score": score,
                })
        
        print(f"  Product Hunt: {len(results)} academic tools found")
    except Exception as e:
        print(f"  [WARN] Product Hunt failed: {e}")
    
    return results


# ============================================================
# 数据源 2：Hacker News Show HN
# ============================================================

def fetch_hn_show():
    """从 HN Show HN 获取新工具展示"""
    results = []
    try:
        story_ids = http_get_json(
            "https://hacker-news.firebaseio.com/v0/showstories.json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        count = 0
        for sid in story_ids[:80]:  # 多检查前 80 条
            if count >= 5:
                break
            try:
                story = http_get_json(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                title = story.get("title", "")
                text = story.get("text", "")
                url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
                
                # Show HN 去掉前缀
                clean_title = re.sub(r'^Show HN:\s*', '', title, flags=re.IGNORECASE)
                
                ok, score = is_research_tool(clean_title, text)
                if ok:
                    results.append({
                        "title": clean_title,
                        "summary": f"Shared on Hacker News Show HN. {re.sub('<.*?>', '', text)[:180].strip() if text else ''}",
                        "url": url,
                        "source": "Hacker News",
                        "icon": "🔶",
                        "date": datetime.utcfromtimestamp(story.get("time", 0)).strftime("%Y-%m-%d"),
                        "score": score,
                    })
                    count += 1
            except:
                continue
        
        print(f"  HN Show HN: {len(results)} academic tools found")
    except Exception as e:
        print(f"  [WARN] HN Show HN failed: {e}")
    
    return results


# ============================================================
# 数据源 3：GitHub（专门搜索学术工具 repo）
# ============================================================

def fetch_github_academic():
    """从 GitHub 搜索最近新建的学术工具"""
    results = []
    try:
        from datetime import timedelta
        cutoff = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        queries = [
            f"topic:research-tools created:>{cutoff}",
            f"topic:academic created:>{cutoff}",
            f"topic:citation-manager created:>{cutoff}",
            f"pdf research assistant created:>{cutoff}",
            f"literature review tool created:>{cutoff}",
        ]
        
        seen = set()
        for query in queries:
            if len(results) >= 5:
                break
            try:
                data = http_get_json(
                    "https://api.github.com/search/repositories",
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "AcademicRadar/1.0",
                    }
                )
                # 实际请求需要带参数，这里修正：
                import urllib.parse
                url_with_params = (
                    "https://api.github.com/search/repositories?"
                    + urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": "5"})
                )
                data = http_get_json(url_with_params, headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "AcademicRadar/1.0",
                })
                
                for repo in data.get("items", [])[:3]:
                    repo_url = repo.get("html_url", "")
                    if repo_url in seen:
                        continue
                    seen.add(repo_url)
                    
                    name = repo.get("full_name", "")
                    desc = repo.get("description", "") or ""
                    stars = repo.get("stargazers_count", 0)
                    
                    ok, score = is_research_tool(name + " " + desc, "")
                    if ok:
                        results.append({
                            "title": repo.get("name", name),
                            "summary": desc[:200] if desc else f"New GitHub project: {name}",
                            "url": repo_url,
                            "source": "GitHub",
                            "icon": "🐙",
                            "date": datetime.utcnow().strftime("%Y-%m-%d"),
                            "score": score + (1 if stars > 100 else 0),
                            "stars": stars,
                        })
            except Exception as e:
                print(f"    [WARN] GitHub query failed: {e}")
                continue
        
        print(f"  GitHub: {len(results)} academic tools found")
    except Exception as e:
        print(f"  [WARN] GitHub academic fetch failed: {e}")
    
    return results


# ============================================================
# 主函数
# ============================================================

def collect_daily_news(data_dir="data"):
    print("📰 Collecting academic AI tool news...")
    
    all_results = []
    all_results.extend(fetch_product_hunt())
    all_results.extend(fetch_hn_show())
    all_results.extend(fetch_github_academic())
    
    # 去重（按 URL）
    seen_urls = set()
    unique = []
    for item in all_results:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(item)
    
    # 按分数排序，取前 5
    unique.sort(key=lambda x: x.get("score", 0), reverse=True)
    final = unique[:5]
    
    print(f"  ✅ Final: {len(final)} items selected for today's brief")
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output = {"date": today, "news": final}
    
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f"news_{today}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 Saved: {filepath}")
    return filepath


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    collect_daily_news(os.path.join(root_dir, "data"))
