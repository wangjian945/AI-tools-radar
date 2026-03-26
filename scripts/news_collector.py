"""
AI News Brief Collector
采集最新 AI 新闻，生成简短图文简报
数据源：GitHub Trending, arXiv, Hacker News
"""

import json
import os
import re
from datetime import datetime

try:
    import httpx
    def http_get(url, headers=None, params=None, timeout=30):
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json() if 'json' in resp.headers.get('content-type', '') else resp.text
except ImportError:
    import urllib.request
    import urllib.parse
    def http_get(url, headers=None, params=None, timeout=30):
        if params:
            url = url + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode('utf-8')
            ct = resp.headers.get('content-type', '')
            return json.loads(data) if 'json' in ct else data


def fetch_github_trending():
    """从 GitHub API 获取今日热门 AI 项目"""
    news = []
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "topic:artificial-intelligence created:>2026-03-20",
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        data = http_get(url, params=params, headers={"Accept": "application/vnd.github.v3+json"})
        if isinstance(data, str):
            data = json.loads(data)
        
        for repo in data.get("items", [])[:5]:
            news.append({
                "title": repo.get("full_name", ""),
                "summary": repo.get("description", "")[:200] if repo.get("description") else "",
                "url": repo.get("html_url", ""),
                "source": "GitHub",
                "icon": "🐙",
                "stars": repo.get("stargazers_count", 0),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
            })
    except Exception as e:
        print(f"  [WARN] GitHub trending failed: {e}")
    return news


def fetch_arxiv_highlights():
    """从 arXiv API 获取最新 AI 论文亮点"""
    news = []
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.LG",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": "5"
        }
        xml_text = http_get(url, params=params)
        
        # 简单解析 XML
        entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
        for entry in entries[:5]:
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            link_match = re.search(r'<id>(.*?)</id>', entry)
            
            title = title_match.group(1).strip().replace('\n', ' ') if title_match else ""
            summary = summary_match.group(1).strip().replace('\n', ' ')[:200] if summary_match else ""
            url = link_match.group(1).strip() if link_match else ""
            
            if title:
                news.append({
                    "title": title,
                    "summary": summary + "...",
                    "url": url,
                    "source": "arXiv",
                    "icon": "📄",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"  [WARN] arXiv highlights failed: {e}")
    return news


def fetch_hn_ai_news():
    """从 Hacker News API 获取 AI 相关热门"""
    news = []
    try:
        top_ids = http_get("https://hacker-news.firebaseio.com/v0/topstories.json")
        if isinstance(top_ids, str):
            top_ids = json.loads(top_ids)
        
        ai_keywords = ['ai', 'llm', 'gpt', 'claude', 'gemini', 'openai', 'anthropic', 
                       'machine learning', 'deep learning', 'neural', 'transformer',
                       'research', 'paper', 'model']
        
        count = 0
        for story_id in top_ids[:50]:
            if count >= 3:
                break
            try:
                story = http_get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                if isinstance(story, str):
                    story = json.loads(story)
                
                title = story.get("title", "").lower()
                if any(kw in title for kw in ai_keywords):
                    news.append({
                        "title": story.get("title", ""),
                        "summary": f"Score: {story.get('score', 0)} · {story.get('descendants', 0)} comments",
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "Hacker News",
                        "icon": "🔶",
                        "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    })
                    count += 1
            except:
                continue
    except Exception as e:
        print(f"  [WARN] HN news failed: {e}")
    return news


def collect_daily_news(data_dir="data"):
    """采集今日 AI 新闻并保存"""
    print("📰 Collecting AI news...")
    
    all_news = []
    all_news.extend(fetch_github_trending())
    all_news.extend(fetch_arxiv_highlights())
    all_news.extend(fetch_hn_ai_news())
    
    print(f"  📰 Collected {len(all_news)} raw news items")
    
    # 关键词过滤
    research_keywords = [
        'research', 'paper', 'academic', 'citation', 'reference', 'literature', 
        'thesis', 'dissertation', 'latex', 'bibtex', 'zotero', 'mendeley',
        'scholar', 'science', 'arxiv', 'pdf', 'summary', 'reading', 'writing'
    ]
    
    filtered_news = []
    seen_urls = set()
    
    for item in all_news:
        url = item.get('url')
        if url in seen_urls: continue
        seen_urls.add(url)
        
        text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
        if any(kw in text for kw in research_keywords):
            filtered_news.append(item)
    
    # 排序：相关度 > 热度
    filtered_news.sort(key=lambda x: x.get('stars', 0) if x.get('source')=='GitHub' else 0, reverse=True)
    
    final_news = filtered_news[:5]
    print(f"  ✅ Filtered {len(final_news)} academic-relevant items")
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output = {
        "date": today,
        "news": final_news,
    }
    
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f"news_{today}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 Saved: {filepath}")
    return filepath


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    collect_daily_news(os.path.join(root_dir, "data"))
