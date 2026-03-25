"""
AI Tools Radar - HTML Renderer
按 Monash University 风格生成静态 HTML 页面
核心设计：累积式信息库 + 每日新发现 + 分类导航
"""

import json
import os
import sys
import glob
from datetime import datetime

# ============================================================
# 数据加载：合并所有历史数据，去重
# ============================================================

def load_all_tools(data_dir="data"):
    """
    加载所有历史 processed 文件，合并去重
    返回：(all_tools, today_new_tools, featured_tools, all_dates)
    """
    all_tools = {}  # 用 URL 去重
    all_dates = set()
    
    # 按时间顺序加载所有 processed 文件
    pattern = os.path.join(data_dir, "processed_*.json")
    files = sorted(glob.glob(pattern))
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            date = data.get("date", "")
            all_dates.add(date)
            
            for tool in data.get("tools", []):
                url = tool.get("url", "")
                if not url:
                    continue
                
                # 如果工具已存在，保留质量分更高的版本
                if url in all_tools:
                    existing_score = all_tools[url].get("quality_score", 0)
                    new_score = tool.get("quality_score", 0)
                    if new_score > existing_score:
                        all_tools[url] = tool
                else:
                    all_tools[url] = tool
        except Exception as e:
            print(f"  [WARN] Error loading {filepath}: {e}")
    
    # 确定今天的日期
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # 筛选：今日新增 & 精选
    today_new = []
    featured = []
    
    for tool in all_tools.values():
        if tool.get("collected_date", "") == today:
            today_new.append(tool)
        if tool.get("featured", False) or tool.get("quality_score", 0) >= 9:
            featured.append(tool)
    
    tools_list = list(all_tools.values())
    tools_list.sort(key=lambda x: (-x.get("quality_score", 0), x.get("name", "")))
    
    return tools_list, today_new, featured, sorted(all_dates, reverse=True)


# ============================================================
# Monash 风格 HTML 模板
# ============================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tools Radar | Lab Intelligence Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #006DAE;
            --primary-dark: #004B87;
            --primary-light: #E8F4FD;
            --accent: #D93F00;
            --accent-light: #FFF3E0;
            --bg: #FFFFFF;
            --bg-alt: #F5F7FA;
            --text: #1A1A2E;
            --text-secondary: #5A6677;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-lg: 0 4px 14px rgba(0,0,0,0.1);
            --radius: 8px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-alt);
            color: var(--text);
            line-height: 1.6;
            padding-bottom: 60px;
        }}

        /* ---- Header ---- */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 40px 0 80px; /* Extra padding for overlap */
        }}
        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
        }}
        .header h1 {{ font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; }}
        .header-meta {{ margin-top: 16px; opacity: 0.9; font-size: 0.9rem; }}

        /* ---- Sticky Nav ---- */
        .sticky-nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            margin-top: -40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .nav-inner {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
            display: flex;
            gap: 20px;
            overflow-x: auto;
            white-space: nowrap;
            scrollbar-width: none;
        }}
        .nav-btn {{
            padding: 16px 0;
            border: none;
            background: none;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }}
        .nav-btn:hover, .nav-btn.active {{ color: var(--primary); border-bottom-color: var(--primary); }}

        /* ---- Main Layout ---- */
        .container {{
            max-width: 1200px;
            margin: 32px auto;
            padding: 0 32px;
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 40px;
        }}

        /* Sidebar (Category Filter) */
        .sidebar {{
            position: sticky;
            top: 80px;
            height: fit-content;
        }}
        .sidebar-title {{
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}
        .cat-btn {{
            display: block;
            width: 100%;
            text-align: left;
            padding: 8px 12px;
            margin-bottom: 4px;
            border-radius: var(--radius);
            border: none;
            background: none;
            color: var(--text);
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }}
        .cat-btn:hover {{ background: var(--bg); color: var(--primary); }}
        .cat-btn.active {{ background: var(--primary-light); color: var(--primary); font-weight: 600; }}

        /* Content Area */
        .content {{ min-height: 80vh; }}

        /* ---- Section: Featured / Today ---- */
        .hero-section {{
            margin-bottom: 40px;
        }}
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border);
        }}
        .section-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--primary-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* Tool Cards */
        .tool-card {{
            background: white;
            border-radius: var(--radius);
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            gap: 24px;
        }}
        .tool-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-light);
        }}
        
        .card-main {{ flex: 1; }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .tool-name {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }}
        .tool-cat {{
            font-size: 0.75rem;
            background: var(--bg-alt);
            padding: 4px 10px;
            border-radius: 20px;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .one-liner {{ font-size: 1rem; color: var(--text); margin-bottom: 12px; line-height: 1.5; }}
        
        .features {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        .feature-tag {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            background: #F1F5F9;
            padding: 4px 10px;
            border-radius: 4px;
        }}

        .card-meta {{
            display: flex;
            gap: 16px;
            font-size: 0.8rem;
            color: var(--text-secondary);
            align-items: center;
        }}
        .btn-visit {{
            margin-left: auto;
            background: var(--primary);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ grid-template-columns: 1fr; }}
            .sidebar {{ display: none; }} /* Mobile hide sidebar for now */
            .tool-card {{ flex-direction: column; gap: 16px; }}
        }}
    </style>
</head>
<body>

<header class="header">
    <div class="header-inner">
        <h1>🔬 AI Tools Radar</h1>
        <div class="header-meta">
            <span>📅 {date}</span> · 
            <span>📊 {total_tools} Tools</span> · 
            <span>🆕 {today_new_count} New Today</span>
        </div>
    </div>
</header>

<div class="sticky-nav">
    <div class="nav-inner">
        <button class="nav-btn active" onclick="showView('all')">📚 All Tools</button>
        <button class="nav-btn" onclick="showView('today')">🆕 Today's New</button>
        <button class="nav-btn" onclick="showView('featured')">⭐ Featured</button>
        <button class="nav-btn" onclick="showView('timeline')">📅 Timeline</button>
    </div>
</div>

<div class="container">
    <aside class="sidebar">
        <div class="sidebar-title">Categories</div>
        <button class="cat-btn active" onclick="filterCat('all')">All Categories</button>
        {category_nav}
    </aside>

    <main class="content">
        <!-- View: All Tools (Default) -->
        <div id="view-all" class="view active">
            {all_sections_html}
        </div>

        <!-- View: Today -->
        <div id="view-today" class="view">
            <div class="section-header">
                <div class="section-title">🆕 Discovered Today ({date})</div>
            </div>
            {today_html}
        </div>

        <!-- View: Featured -->
        <div id="view-featured" class="view">
            <div class="section-header">
                <div class="section-title">⭐ Featured Tools</div>
            </div>
            {featured_html}
        </div>
    </main>
</div>

<script>
function showView(viewName) {{
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.getElementById('view-' + viewName).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    event.target.classList.add('active');
    
    window.scrollTo(0, 0);
}}

function filterCat(category) {{
    document.querySelectorAll('.cat-btn').forEach(el => el.classList.remove('active'));
    event.target.classList.add('active');
    
    // Hide/Show tool cards based on category
    document.querySelectorAll('.tool-card').forEach(card => {{
        if (category === 'all' || card.dataset.category === category) {{
            card.style.display = 'flex';
        }} else {{
            card.style.display = 'none';
        }}
    }});
    
    // Hide empty sections
    document.querySelectorAll('.category-group').forEach(group => {{
        if (category === 'all' || group.dataset.category === category) {{
            group.style.display = 'block';
        }} else {{
            group.style.display = 'none';
        }}
    }});
}}
</script>

</body>
</html>"""


CARD_TEMPLATE = """
<div class="tool-card" data-category="{category}">
    <div class="card-main">
        <div class="card-header">
            <a href="{url}" target="_blank" class="tool-name">{name}</a>
            <span class="tool-cat">{category}</span>
        </div>
        <div class="one-liner">{one_liner}</div>
        <div class="features">
            {features_html}
        </div>
        <div class="card-meta">
            <span>{pricing}</span>
            <span>{source}</span>
            {date_badge}
            <a href="{url}" target="_blank" class="btn-visit">Visit Site →</a>
        </div>
    </div>
</div>"""


CATEGORY_ICONS = {
    "Literature Review": "📚",
    "Data Analysis": "📊",
    "Writing & Drafting": "✍️",
    "Visualization": "📈",
    "Peer Review": "💬",
    "Coding & Dev": "💻",
    "Experiment Design": "🧪",
    "Other": "🔧"
}


def render_tool_card(tool):
    features = tool.get("key_features", [])[:3]
    features_html = "".join(f'<span class="feature-tag">{f}</span>' for f in features)
    
    date_str = tool.get("collected_date", "")
    date_badge = f'<span>📅 {date_str}</span>' if date_str else ""
    
    return CARD_TEMPLATE.format(
        name=tool.get("name", "Unknown"),
        category=tool.get("category", "Other"),
        one_liner=tool.get("one_liner", ""),
        features_html=features_html,
        pricing=tool.get("pricing", "Unknown"),
        source=tool.get("source", "Unknown"),
        date_badge=date_badge,
        url=tool.get("url", "#")
    )


def render_page(data_dir="data", output_dir="site"):
    all_tools, today_new, featured, all_dates = load_all_tools(data_dir)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # 侧边栏导航
    categories = {}
    for tool in all_tools:
        cat = tool.get("category", "Other")
        categories.setdefault(cat, []).append(tool)
        
    cat_nav_html = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        cat_nav_html += f'<button class="cat-btn" onclick="filterCat(\'{cat}\')">{icon} {cat}</button>\n'
    
    # 全部工具列表（按分类分组）
    all_sections_html = ""
    for cat in sorted(categories.keys()):
        tools = categories[cat]
        cards = "\n".join(render_tool_card(t) for t in tools)
        icon = CATEGORY_ICONS.get(cat, "🔧")
        all_sections_html += f"""
        <div class="category-group" data-category="{cat}">
            <div class="section-header">
                <div class="section-title">{icon} {cat}</div>
            </div>
            {cards}
        </div>"""
        
    # 今日新增
    today_html = "\n".join(render_tool_card(t) for t in today_new) if today_new else "<p>No new tools discovered today.</p>"
    
    # 精选
    featured_html = "\n".join(render_tool_card(t) for t in featured) if featured else "<p>No featured tools yet.</p>"
    
    html = HTML_TEMPLATE.format(
        date=today,
        total_tools=len(all_tools),
        today_new_count=len(today_new),
        category_nav=cat_nav_html,
        all_sections_html=all_sections_html,
        today_html=today_html,
        featured_html=featured_html
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"🎨 Page rendered: {output_path}")


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")
    output_dir = os.path.join(root_dir, "site")
    render_page(data_dir, output_dir)
