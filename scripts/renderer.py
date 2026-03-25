"""
AI Tools Radar - HTML Renderer
按 Monash University 风格生成静态 HTML 页面
"""

import json
import os
import sys
from datetime import datetime

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
        }}
        .header-meta span {{ display: flex; align-items: center; gap: 6px; }}

        /* ---- Nav / Filter ---- */
        .filter-bar {{
            max-width: 1200px;
            margin: -20px auto 0;
            padding: 0 32px;
            position: relative;
            z-index: 10;
        }}
        .filter-inner {{
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            padding: 16px 24px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 18px;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        /* ---- Main Content ---- */
        .main {{
            max-width: 1200px;
            margin: 32px auto;
            padding: 0 32px;
        }}

        .section-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--primary-dark);
            margin: 32px 0 16px;
            padding-left: 12px;
            border-left: 3px solid var(--primary);
        }}

        /* ---- Tool Card ---- */
        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
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
        .badge-category {{
            background: var(--primary-light);
            color: var(--primary);
        }}
        .badge-source {{
            background: #FFF3E0;
            color: #E65100;
        }}
        .badge-free {{
            background: #E8F5E9;
            color: #2E7D32;
        }}
        .badge-paid {{
            background: #FBE9E7;
            color: #BF360C;
        }}

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
        }}
        .tool-card .card-footer a {{
            font-size: 0.82rem;
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}
        .tool-card .card-footer a:hover {{
            text-decoration: underline;
        }}

        .stars {{ color: #F59E0B; font-size: 0.82rem; }}

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
            <span>📊 {total_tools} Tools Tracked</span>
            <span>🔄 Auto-updated daily via GitHub Actions</span>
        </div>
    </div>
</header>

<div class="filter-bar">
    <div class="filter-inner">
        <button class="filter-btn active" onclick="filterTools('all')">All</button>
        {filter_buttons}
    </div>
</div>

<main class="main">
    {sections_html}
</main>

<footer class="footer">
    <p>Built with ❤️ for the Lab · Auto-updated daily · 
    <a href="https://github.com/wangjian945/AI-tools-radar">View Source</a></p>
    <p style="margin-top:8px">Last build: {build_time}</p>
</footer>

<script>
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
            const hasVisible = section.querySelectorAll(`.tool-card[data-category="${{category}}"]`).length > 0;
            section.style.display = hasVisible ? '' : 'none';
        }}
    }});
}}
</script>

</body>
</html>"""


CARD_TEMPLATE = """
<div class="tool-card" data-category="{category}">
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


def render_tool_card(tool):
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
    )


def render_page(processed_data_path, output_dir="site"):
    """渲染完整 HTML 页面"""
    with open(processed_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tools = data.get("tools", [])
    date_str = data.get("date", datetime.utcnow().strftime('%Y-%m-%d'))
    
    # 按分类分组
    categories = {}
    for tool in tools:
        cat = tool.get("category", "Other")
        categories.setdefault(cat, []).append(tool)
    
    # 生成筛选按钮
    filter_buttons = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        filter_buttons += f'<button class="filter-btn" onclick="filterTools(\'{cat}\')">{icon} {cat} ({len(categories[cat])})</button>\n        '
    
    # 生成各分类的卡片区域
    sections_html = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        cards_html = "\n".join(render_tool_card(t) for t in categories[cat])
        sections_html += f"""
    <div class="category-section" data-section="{cat}">
        <h2 class="section-title">{icon} {cat}</h2>
        <div class="tools-grid">
            {cards_html}
        </div>
    </div>
"""
    
    # 渲染完整页面
    html = HTML_TEMPLATE.format(
        date=date_str,
        total_tools=len(tools),
        filter_buttons=filter_buttons,
        sections_html=sections_html,
        build_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"🎨 Page rendered: {output_path}")
    print(f"   {len(tools)} tools in {len(categories)} categories")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        proc_files = sorted([f for f in os.listdir(data_dir) if f.startswith("processed_")])
        if not proc_files:
            print("❌ No processed data found. Run processor.py first.")
            sys.exit(1)
        proc_path = os.path.join(data_dir, proc_files[-1])
    else:
        proc_path = sys.argv[1]
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "site")
    render_page(proc_path, output_dir)
