"""
AI Tools Radar - HTML Renderer
按 Monash University 风格生成静态 HTML 页面
核心设计：累积式信息库 + 每日新发现
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
    返回：(all_tools, today_new_tools, all_dates)
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
    
    # 标记今日新增的工具
    today_new = []
    for tool in all_tools.values():
        if tool.get("collected_date", "") == today:
            today_new.append(tool)
    
    tools_list = list(all_tools.values())
    tools_list.sort(key=lambda x: (-x.get("quality_score", 0), x.get("name", "")))
    
    return tools_list, today_new, sorted(all_dates, reverse=True)


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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #006DAE;
            --primary-dark: #004B87;
            --primary-light: #E8F4FD;
            --accent: #D93F00;
            --bg: #FFFFFF;
            --bg-alt: #F5F7FA;
            --text: #1A1A2E;
            --text-secondary: #5A6677;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
            --shadow-lg: 0 4px 14px rgba(0,0,0,0.1);
            --radius: 8px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-alt);
            color: var(--text);
            line-height: 1.6;
        }}

        /* ---- Header ---- */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 48px 0 40px;
        }}
        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
        }}
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header p {{
            margin-top: 8px;
            font-size: 1.05rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        .header-meta {{
            margin-top: 20px;
            display: flex;
            gap: 24px;
            font-size: 0.85rem;
            opacity: 0.8;
            flex-wrap: wrap;
        }}
        .header-meta span {{ display: flex; align-items: center; gap: 6px; }}

        /* ---- Tab Switcher ---- */
        .tab-bar {{
            max-width: 1200px;
            margin: -20px auto 0;
            padding: 0 32px;
            position: relative;
            z-index: 10;
        }}
        .tab-inner {{
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            padding: 12px 24px;
            display: flex;
            gap: 0;
        }}
        .tab-btn {{
            padding: 10px 24px;
            border: none;
            background: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-secondary);
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{ color: var(--primary); }}
        .tab-btn.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
            font-weight: 600;
        }}

        /* ---- Filter Bar ---- */
        .filter-bar {{
            max-width: 1200px;
            margin: 16px auto 0;
            padding: 0 32px;
        }}
        .filter-inner {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-label {{
            font-size: 0.82rem;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        .filter-btn {{
            padding: 6px 16px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        /* ---- Search ---- */
        .search-box {{
            max-width: 1200px;
            margin: 16px auto 0;
            padding: 0 32px;
        }}
        .search-input {{
            width: 100%;
            padding: 12px 20px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 0.92rem;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-input:focus {{
            border-color: var(--primary);
        }}

        /* ---- Main Content ---- */
        .main {{
            max-width: 1200px;
            margin: 24px auto 32px;
            padding: 0 32px;
        }}

        .view {{ display: none; }}
        .view.active {{ display: block; }}

        .section-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--primary-dark);
            margin: 28px 0 16px;
            padding-left: 12px;
            border-left: 3px solid var(--primary);
        }}

        /* ---- Today Banner ---- */
        .today-banner {{
            background: linear-gradient(135deg, #E8F4FD 0%, #FFF3E0 100%);
            border: 1px solid var(--primary-light);
            border-radius: var(--radius);
            padding: 20px 24px;
            margin-bottom: 24px;
        }}
        .today-banner h3 {{
            color: var(--primary-dark);
            font-size: 1.1rem;
            margin-bottom: 4px;
        }}
        .today-banner p {{
            color: var(--text-secondary);
            font-size: 0.88rem;
        }}

        /* ---- Tool Card ---- */
        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .tool-card {{
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
            border-top: 3px solid var(--primary);
            display: flex;
            flex-direction: column;
        }}
        .tool-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        .tool-card.new-today {{
            border-top-color: var(--accent);
        }}
        .tool-card.new-today::after {{
            content: "🆕 NEW";
            position: absolute;
            top: 8px;
            right: 8px;
            background: var(--accent);
            color: white;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .tool-card {{ position: relative; }}

        .tool-card .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        .tool-card h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text);
        }}
        .tool-card h3 a {{
            color: inherit;
            text-decoration: none;
        }}
        .tool-card h3 a:hover {{
            color: var(--primary);
        }}

        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}
        .badge-category {{ background: var(--primary-light); color: var(--primary); }}
        .badge-source {{ background: #FFF3E0; color: #E65100; }}
        .badge-free {{ background: #E8F5E9; color: #2E7D32; }}
        .badge-paid {{ background: #FBE9E7; color: #BF360C; }}
        .badge-date {{ background: #F3F4F6; color: #6B7280; }}

        .tool-card .one-liner {{
            color: var(--text-secondary);
            font-size: 0.92rem;
            margin-bottom: 14px;
            flex-grow: 1;
        }}

        .tool-card .features {{
            list-style: none;
            margin-bottom: 16px;
        }}
        .tool-card .features li {{
            font-size: 0.82rem;
            color: var(--text-secondary);
            padding: 3px 0;
        }}
        .tool-card .features li::before {{
            content: "✦ ";
            color: var(--primary);
            font-size: 0.7rem;
        }}

        .tool-card .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 14px;
            border-top: 1px solid var(--border);
            margin-top: auto;
        }}
        .tool-card .card-footer .meta {{
            font-size: 0.78rem;
            color: var(--text-secondary);
            display: flex;
            gap: 6px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .tool-card .card-footer a {{
            font-size: 0.82rem;
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}
        .tool-card .card-footer a:hover {{ text-decoration: underline; }}

        .stars {{ color: #F59E0B; font-size: 0.82rem; }}

        /* ---- Timeline ---- */
        .timeline-date {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--primary);
            margin: 28px 0 12px;
            padding: 8px 16px;
            background: var(--primary-light);
            border-radius: var(--radius);
            display: inline-block;
        }}

        /* ---- Empty State ---- */
        .empty-state {{
            text-align: center;
            padding: 48px;
            color: var(--text-secondary);
        }}

        /* ---- Stats ---- */
        .stats-bar {{
            display: flex;
            gap: 32px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-num {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
        }}
        .stat-label {{
            font-size: 0.78rem;
            color: var(--text-secondary);
        }}

        /* ---- Footer ---- */
        .footer {{
            text-align: center;
            padding: 40px 32px;
            color: var(--text-secondary);
            font-size: 0.82rem;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}

        /* ---- Responsive ---- */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.5rem; }}
            .tools-grid {{ grid-template-columns: 1fr; }}
            .header-meta {{ flex-direction: column; gap: 8px; }}
            .tab-btn {{ padding: 8px 14px; font-size: 0.85rem; }}
        }}
    </style>
</head>
<body>

<header class="header">
    <div class="header-inner">
        <h1>🔬 AI Tools Radar</h1>
        <p>AI-Powered Research Tools — Daily Intelligence for the Lab</p>
        <div class="header-meta">
            <span>📅 Updated: {date}</span>
            <span>📊 {total_tools} Tools in Database</span>
            <span>🆕 {today_new_count} New Today</span>
            <span>📁 {total_dates} Days Tracked</span>
        </div>
    </div>
</header>

<div class="tab-bar">
    <div class="tab-inner">
        <button class="tab-btn active" onclick="switchTab('database')">📚 Tools Database</button>
        <button class="tab-btn" onclick="switchTab('today')">🆕 Today's Discoveries</button>
        <button class="tab-btn" onclick="switchTab('timeline')">📅 Timeline</button>
    </div>
</div>

<div class="search-box">
    <input type="text" class="search-input" placeholder="🔍 Search tools by name, category, or feature..." oninput="searchTools(this.value)">
</div>

<div class="filter-bar">
    <div class="filter-inner">
        <span class="filter-label">Filter:</span>
        <button class="filter-btn active" onclick="filterTools('all')">All</button>
        {filter_buttons}
    </div>
</div>

<main class="main">
    <!-- Tab 1: Full Database -->
    <div id="view-database" class="view active">
        <div class="stats-bar">
            {stats_html}
        </div>
        {database_sections_html}
    </div>

    <!-- Tab 2: Today's New -->
    <div id="view-today" class="view">
        {today_html}
    </div>

    <!-- Tab 3: Timeline -->
    <div id="view-timeline" class="view">
        {timeline_html}
    </div>
</main>

<footer class="footer">
    <p>Built with Jian for the Lab · Auto-updated daily · 
    <a href="https://github.com/wangjian945/AI-tools-radar">View Source</a></p>
    <p style="margin-top:8px">Last build: {build_time}</p>
</footer>

<script>
function switchTab(tab) {{
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById('view-' + tab).classList.add('active');
}}

function filterTools(category) {{
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.tool-card').forEach(card => {{
        if (category === 'all' || card.dataset.category === category) {{
            card.style.display = '';
        }} else {{
            card.style.display = 'none';
        }}
    }});
    
    document.querySelectorAll('.category-section').forEach(section => {{
        if (category === 'all') {{
            section.style.display = '';
        }} else {{
            const cards = section.querySelectorAll('.tool-card');
            const hasVisible = Array.from(cards).some(c => c.style.display !== 'none');
            section.style.display = hasVisible ? '' : 'none';
        }}
    }});
}}

function searchTools(query) {{
    query = query.toLowerCase().trim();
    document.querySelectorAll('.tool-card').forEach(card => {{
        const text = card.textContent.toLowerCase();
        card.style.display = (!query || text.includes(query)) ? '' : 'none';
    }});
    document.querySelectorAll('.category-section').forEach(section => {{
        const cards = section.querySelectorAll('.tool-card');
        const hasVisible = Array.from(cards).some(c => c.style.display !== 'none');
        section.style.display = hasVisible ? '' : 'none';
    }});
}}
</script>

</body>
</html>"""


CARD_TEMPLATE = """
<div class="tool-card{new_class}" data-category="{category}">
    <div class="card-header">
        <h3><a href="{url}" target="_blank">{name}</a></h3>
        <span class="badge badge-category">{category}</span>
    </div>
    <p class="one-liner">{one_liner}</p>
    <ul class="features">
        {features_html}
    </ul>
    <div class="card-footer">
        <div class="meta">
            <span class="badge badge-source">{source}</span>
            {pricing_badge}
            {stars_html}
            <span class="badge badge-date">{collected_date}</span>
        </div>
        <a href="{url}" target="_blank">Explore →</a>
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


def render_tool_card(tool, is_new=False):
    """渲染单个工具卡片"""
    features_html = "\n        ".join(
        f'<li>{f}</li>' for f in tool.get("key_features", [])[:4]
    )
    
    pricing = tool.get("pricing", "Unknown")
    if pricing in ("Free", "Open Source"):
        pricing_badge = f'<span class="badge badge-free">{pricing}</span>'
    elif pricing == "Paid":
        pricing_badge = '<span class="badge badge-paid">Paid</span>'
    else:
        pricing_badge = f'<span class="badge" style="background:#F3F4F6;color:#6B7280">{pricing}</span>'
    
    stars = tool.get("stars", 0)
    stars_html = f'<span class="stars">⭐ {stars:,}</span>' if stars else ""
    
    return CARD_TEMPLATE.format(
        name=tool.get("name", "Unknown"),
        category=tool.get("category", "Other"),
        one_liner=tool.get("one_liner", ""),
        features_html=features_html,
        source=tool.get("source", ""),
        pricing_badge=pricing_badge,
        stars_html=stars_html,
        url=tool.get("url", "#"),
        collected_date=tool.get("collected_date", ""),
        new_class=" new-today" if is_new else "",
    )


def render_page(data_dir="data", output_dir="site"):
    """渲染完整 HTML 页面（累积式）"""
    
    # 加载所有历史数据
    all_tools, today_new, all_dates = load_all_tools(data_dir)
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    today_urls = set(t.get("url", "") for t in today_new)
    
    print(f"  📊 Total tools in database: {len(all_tools)}")
    print(f"  🆕 New today: {len(today_new)}")
    print(f"  📅 Days tracked: {len(all_dates)}")
    
    # === 按分类分组 ===
    categories = {}
    for tool in all_tools:
        cat = tool.get("category", "Other")
        categories.setdefault(cat, []).append(tool)
    
    # === 生成筛选按钮 ===
    filter_buttons = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        filter_buttons += f'<button class="filter-btn" onclick="filterTools(\'{cat}\')">{icon} {cat} ({len(categories[cat])})</button>\n        '
    
    # === 生成统计 ===
    stats_html = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        stats_html += f"""
        <div class="stat-item">
            <div class="stat-num">{len(categories[cat])}</div>
            <div class="stat-label">{icon} {cat}</div>
        </div>"""
    
    # === Tab1: 完整数据库（按分类） ===
    database_sections_html = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        cards_html = "\n".join(
            render_tool_card(t, is_new=(t.get("url", "") in today_urls))
            for t in categories[cat]
        )
        database_sections_html += f"""
    <div class="category-section" data-section="{cat}">
        <h2 class="section-title">{icon} {cat}</h2>
        <div class="tools-grid">
            {cards_html}
        </div>
    </div>"""
    
    # === Tab2: 今日新发现 ===
    if today_new:
        today_cards = "\n".join(render_tool_card(t, is_new=True) for t in today_new)
        today_html = f"""
        <div class="today-banner">
            <h3>🆕 {len(today_new)} New Tools Discovered Today</h3>
            <p>These tools were found during today's automated scan.</p>
        </div>
        <div class="tools-grid">
            {today_cards}
        </div>"""
    else:
        today_html = """
        <div class="empty-state">
            <h3>📭 No new tools discovered today</h3>
            <p>Check back tomorrow — the pipeline runs daily at 08:00 Beijing Time.</p>
        </div>"""
    
    # === Tab3: 时间线 ===
    timeline_html = ""
    tools_by_date = {}
    for tool in all_tools:
        d = tool.get("collected_date", "unknown")
        tools_by_date.setdefault(d, []).append(tool)
    
    for date in sorted(tools_by_date.keys(), reverse=True):
        tools = tools_by_date[date]
        cards = "\n".join(render_tool_card(t) for t in tools)
        timeline_html += f"""
        <div class="timeline-date">📅 {date} — {len(tools)} tool(s)</div>
        <div class="tools-grid">
            {cards}
        </div>"""
    
    # === 渲染 ===
    html = HTML_TEMPLATE.format(
        date=today,
        total_tools=len(all_tools),
        today_new_count=len(today_new),
        total_dates=len(all_dates) if all_dates else 1,
        filter_buttons=filter_buttons,
        stats_html=stats_html,
        database_sections_html=database_sections_html,
        today_html=today_html,
        timeline_html=timeline_html,
        build_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"🎨 Page rendered: {output_path}")
    return output_path


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")
    output_dir = os.path.join(root_dir, "site")
    render_page(data_dir, output_dir)
