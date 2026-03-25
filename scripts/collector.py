"""
AI Research Tools Collector
从多个数据源采集最新AI科研工具信息
"""

import json
import re
import os
import sys
from datetime import datetime, timedelta

# 尝试导入 httpx，如果没有就用 requests
try:
    import httpx
    def http_get(url, headers=None, params=None, timeout=30):
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json() if 'json' in resp.headers.get('content-type', '') else resp.text
    def http_get_text(url, headers=None, timeout=30):
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
except ImportError:
    import urllib.request
    import urllib.parse
    def http_get(url, headers=None, params=None, timeout=30):
        if params:
            url = url + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode('utf-8')
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
    def http_get_text(url, headers=None, timeout=30):
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')


def fetch_github_trending(days_back=7, min_stars=20):
    """
    从GitHub搜索最近的AI科研工具仓库
    """
    since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    queries = [
        f"topic:ai-tools pushed:>{since_date} stars:>{min_stars}",
        f"topic:research-tools pushed:>{since_date} stars:>{min_stars}",
        f"AI research tool pushed:>{since_date} stars:>{min_stars}",
        f"scientific paper tool pushed:>{since_date} stars:>{min_stars}",
        f"literature review AI pushed:>{since_date} stars:>{min_stars}",
    ]
    
    tools = []
    seen_repos = set()
    
    for query in queries:
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": 15
            }
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            # 如果有GitHub Token，使用它来提高限额
            gh_token = os.environ.get("GITHUB_TOKEN")
            if gh_token:
                headers["Authorization"] = f"token {gh_token}"
            
            data = http_get(url, headers=headers, params=params)
            
            for item in data.get("items", []):
                repo_name = item["full_name"]
                if repo_name in seen_repos:
                    continue
                seen_repos.add(repo_name)
                
                tools.append({
                    "name": item["name"],
                    "source": "GitHub",
                    "description": item.get("description", ""),
                    "url": item["html_url"],
                    "stars": item["stargazers_count"],
                    "language": item.get("language", "Unknown"),
                    "updated_at": item["updated_at"],
                    "topics": item.get("topics", []),
                })
        except Exception as e:
            print(f"  [WARN] GitHub query failed: {query[:50]}... => {e}")
            continue
    
    # 按星标排序，取top 20
    tools.sort(key=lambda x: x["stars"], reverse=True)
    return tools[:20]


def fetch_arxiv_tools(max_results=15):
    """
    从arXiv搜索最近提到AI工具的论文
    """
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET
    
    # 搜索与AI工具相关的最新论文
    search_query = urllib.parse.quote(
        'all:"AI tool" OR all:"research tool" OR all:"scientific tool" OR '
        'all:"machine learning tool" OR all:"LLM tool"'
    )
    
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query={search_query}&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    
    tools = []
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode('utf-8')
        
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            link = entry.find('atom:id', ns).text.strip()
            published = entry.find('atom:published', ns).text.strip()
            
            tools.append({
                "name": title[:100],
                "source": "arXiv",
                "description": summary[:500],
                "url": link,
                "published": published,
            })
    except Exception as e:
        print(f"  [WARN] arXiv fetch failed: {e}")
    
    return tools


def fetch_daily_tools():
    """
    主采集函数：汇总所有数据源
    """
    print("=" * 60)
    print(f"🔍 AI Tools Collection - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    all_tools = []
    
    # 1. GitHub Trending
    print("\n📦 Fetching from GitHub...")
    gh_tools = fetch_github_trending()
    print(f"   Found {len(gh_tools)} tools from GitHub")
    all_tools.extend(gh_tools)
    
    # 2. arXiv
    print("\n📄 Fetching from arXiv...")
    arxiv_tools = fetch_arxiv_tools()
    print(f"   Found {len(arxiv_tools)} papers from arXiv")
    all_tools.extend(arxiv_tools)
    
    print(f"\n✅ Total collected: {len(all_tools)} items")
    
    return all_tools


def save_raw_data(tools, output_dir="data"):
    """
    保存原始采集数据
    """
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    filepath = os.path.join(output_dir, f"raw_{date_str}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            "date": date_str,
            "collected_at": datetime.utcnow().isoformat(),
            "total": len(tools),
            "tools": tools
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Raw data saved to {filepath}")
    return filepath


if __name__ == "__main__":
    tools = fetch_daily_tools()
    save_raw_data(tools)
