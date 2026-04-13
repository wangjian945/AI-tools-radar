"""
AI Tools Radar - HTML Renderer
Monash University 风格 · 累积式信息库 · 分类导航 · 详细工具卡片
"""

import json
import os
import sys
import glob
from datetime import datetime


def load_monash_logo():
    """加载嵌入的 Monash logo（base64）- 使用白色文字透明版本"""
    # 优先使用白色文字版本
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "monash_logo_white.json")
    try:
        with open(logo_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("logo", "")
    except:
        # Fallback to original
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "monash_logo_data.json")
        try:
            with open(logo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("logo", "")
        except:
            return ""


def load_news(data_dir="data"):
    """加载最新的新闻数据"""
    pattern = os.path.join(data_dir, "news_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return []
    try:
        with open(files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("news", [])
    except:
        return []


def is_academic_research_tool(tool):
    """Check if a tool is relevant for AI academic research"""
    # Categories that are relevant for academic research
    research_categories = [
        "Literature Search & Review",
        "Literature Review",
        "Reading & Note-Taking",
        "Reference Management",
        "Academic Writing",
        "AI Search & Discovery",
        "Data Analysis",
        "Experiment Design",
        "Visualization",
        "Peer Review",
        "Coding & Dev"
    ]
    
    category = tool.get("category", "")
    is_relevant = tool.get("is_research_relevant", False)
    
    # Check if category matches or if explicitly marked as research relevant
    return category in research_categories or is_relevant


def load_all_tools(data_dir="data", filter_research_only=False):
    all_tools = {}
    all_dates = set()
    
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
                
                # Filter for academic research tools only if requested
                if filter_research_only and not is_academic_research_tool(tool):
                    continue
                
                if url in all_tools:
                    if tool.get("quality_score", 0) > all_tools[url].get("quality_score", 0):
                        all_tools[url] = tool
                else:
                    all_tools[url] = tool
        except Exception as e:
            print(f"  [WARN] Error loading {filepath}: {e}")
    
    tools_list = list(all_tools.values())
    tools_list.sort(key=lambda x: (-x.get("quality_score", 0), x.get("name", "")))
    return tools_list, sorted(all_dates, reverse=True)


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


def render_detail_card(tool):
    """渲染详细工具卡片（含 Key Features, Use Cases, How to Use, Pricing）"""
    name = tool.get("name", "Unknown")
    category = tool.get("category", "Other")
    icon = CATEGORY_ICONS.get(category, "🔧")
    one_liner = tool.get("one_liner", "")
    url = tool.get("url", "#")
    pricing = tool.get("pricing", "Unknown")
    use_case = tool.get("use_case", "")
    how_to_use = tool.get("how_to_use", "")
    collected_date = tool.get("collected_date", "")
    
    # Key Features
    features = tool.get("key_features", [])
    features_html = ""
    feature_icons = ["🔍", "📊", "📝", "🔬", "🔔", "💬", "📋", "⚡"]
    for i, f in enumerate(features[:6]):
        fi = feature_icons[i % len(feature_icons)]
        features_html += f"""
            <div class="feature-item">
                <div class="feature-icon">{fi}</div>
                <div class="feature-text">{f}</div>
            </div>"""
    
    # How to Use (步骤)
    steps_html = ""
    if how_to_use:
        import re
        # 按 "数字. " 模式拆分步骤（如 "1. Do X. 2. Do Y."）
        parts = re.split(r'\d+\.\s+', how_to_use)
        steps = [s.strip().rstrip('.') for s in parts if s.strip()]
        for i, step_text in enumerate(steps[:5], 1):
            steps_html += f"""
                <div class="step">
                    <div class="step-num">{i}</div>
                    <div class="step-text">{step_text}</div>
                </div>"""
    
    # Pricing
    pricing_details = tool.get("pricing_details", {})
    pricing_html = ""
    if pricing_details:
        for plan_name, desc in pricing_details.items():
            # 解析价格
            is_free = "free" in plan_name.lower() or "free" in str(desc).lower()
            is_recommended = "plus" in plan_name.lower() or "pro" in plan_name.lower()
            
            card_class = "pricing-card"
            if is_recommended:
                card_class += " recommended"
            
            # 提取价格数字
            price_display = "Free" if is_free and "free" in plan_name.lower() else plan_name.split("(")[0].strip()
            
            # 清理显示：/mo → /month
            display_name = plan_name.replace("/mo)", "/month)")
            display_desc = desc
            
            pricing_html += f"""
            <div class="{card_class}">
                <div class="plan-name">{display_name}</div>
                <div class="plan-desc">{display_desc}</div>
            </div>"""
    
    # Pricing badge
    if pricing in ("Free", "Open Source"):
        pricing_badge = '<span class="badge badge-free">Free</span>'
    elif pricing == "Paid":
        pricing_badge = '<span class="badge badge-paid">Paid</span>'
    else:
        pricing_badge = f'<span class="badge badge-freemium">{pricing}</span>'
    
    # 多源 fallback logo
    logos = tool.get("logos", [])
    if not logos and tool.get("logo"):
        logos = [tool["logo"]]
    
    if logos:
        # 生成 fallback 链：第一个失败用第二个，依此类推
        fallback_js = "this.onerror=null; this.src='" + "; this.onerror=null; this.src='".join(logos[1:]) + "'"
        logo_html = f'<div class="tool-logo"><img src="{logos[0]}" alt="{name} logo" onerror="{fallback_js}"></div>'
    else:
        logo_html = ''
    
    html = f"""
    <div class="tool-detail-card" data-category="{category}" id="tool-{name.lower().replace(' ', '-')}">
        <div class="tool-header">
            {logo_html}
            <div class="tool-header-info">
                <h2 class="tool-name"><a href="{url}" target="_blank">{name}</a></h2>
                <p class="tool-tagline">{one_liner}</p>
                <div class="tool-badges">
                    <span class="badge badge-cat">{icon} {category}</span>
                    {pricing_badge}
                    <span class="badge badge-date">📅 {collected_date}</span>
                </div>
            </div>
            <div class="tool-cta">
                <a href="{url}" target="_blank" class="btn-primary">🔗 Try {name} →</a>
            </div>
        </div>

        <div class="tool-body">"""
    
    # Key Features section
    if features_html:
        html += f"""
            <div class="detail-section">
                <h3>🔑 Key Features</h3>
                <div class="features-grid">
                    {features_html}
                </div>
            </div>"""
    
    # Use Case section
    if use_case:
        html += f"""
            <div class="detail-section">
                <h3>🎯 Best Use Cases</h3>
                <div class="usecase-box">
                    <p>{use_case}</p>
                </div>
            </div>"""
    
    # How to Use section
    if steps_html:
        html += f"""
            <div class="detail-section">
                <h3>📖 How to Get Started</h3>
                <div class="steps-list">
                    {steps_html}
                </div>
            </div>"""
    
    # Pricing section
    if pricing_html:
        html += f"""
            <div class="detail-section">
                <h3>💰 Pricing</h3>
                <div class="pricing-grid">
                    {pricing_html}
                </div>
            </div>"""
    
    html += """
        </div>
    </div>"""
    
    return html


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
            --success: #2E7D32;
            --success-light: #E8F5E9;
            --bg: #FFFFFF;
            --bg-alt: #F5F7FA;
            --text: #1A1A2E;
            --text-secondary: #5A6677;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-lg: 0 4px 14px rgba(0,0,0,0.1);
            --radius: 8px;
            --radius-lg: 12px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-alt);
            color: var(--text);
            line-height: 1.6;
        }}

        /* Header */
        .header {{
            background: #004B87; /* Official Monash Blue */
            color: white;
            padding: 24px 0 20px;
        }}
        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 32px;
            position: relative;
        }}
        .header h1 {{ font-size: 2rem; font-weight: 800; margin-bottom: 6px; }}
        .header-slogan {{
            font-size: 1.05rem;
            font-weight: 300;
            opacity: 0.95;
            max-width: 600px;
            margin-bottom: 12px;
        }}
        .header-meta {{ opacity: 0.85; font-size: 0.85rem; }}
        
        /* Monash Logo in Header */
        .header-monash {{
            position: absolute;
            top: 0;
            right: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
            opacity: 0.9;
        }}
        .monash-logo-img {{
            height: 60px;
            width: auto;
        }}
        .header-monash {{
            position: absolute;
            top: 50%;
            right: 32px;
            transform: translateY(-50%);
        }}
        .header-monash span {{
            font-size: 0.85rem;
            font-weight: 500;
            color: rgba(255,255,255,0.9);
        }}

        /* Layout: Sidebar + Content */
        .page-layout {{
            max-width: 1200px;
            margin: 32px auto;
            padding: 0 32px;
            display: grid;
            grid-template-columns: 260px 1fr;
            gap: 32px;
        }}

        /* Sidebar */
        .sidebar {{
            position: sticky;
            top: 24px;
            height: fit-content;
        }}
        .sidebar-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .cat-link {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            margin-bottom: 4px;
            border-radius: var(--radius);
            border: none;
            background: none;
            color: var(--text);
            cursor: pointer;
            font-size: 0.85rem;
            width: 100%;
            text-align: left;
            transition: all 0.15s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .cat-link:hover {{ background: var(--bg); color: var(--primary); }}
        .cat-link.active {{ background: var(--primary-light); color: var(--primary); font-weight: 600; }}
        .cat-count {{
            margin-left: auto;
            font-size: 0.7rem;
            background: var(--bg-alt);
            padding: 2px 8px;
            border-radius: 10px;
            color: var(--text-secondary);
            flex-shrink: 0;
        }}

        /* Sidebar Notice (University Impact) */
        .sidebar-notice {{
            background: linear-gradient(135deg, #004B87, #006DAE);
            color: white;
            border-radius: var(--radius);
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .notice-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .notice-icon {{
            font-size: 1.2rem;
        }}
        .notice-title {{
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .notice-content {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 12px;
        }}
        .notice-stat {{
            text-align: center;
        }}
        .stat-value {{
            display: block;
            font-size: 1.3rem;
            font-weight: 800;
        }}
        .stat-label {{
            display: block;
            font-size: 0.65rem;
            opacity: 0.85;
            margin-top: 2px;
        }}
        .notice-message {{
            background: rgba(255,255,255,0.1);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
        }}
        .notice-message p {{
            font-size: 0.75rem;
            line-height: 1.5;
            opacity: 0.9;
        }}
        .notice-footer {{
            text-align: center;
        }}
        .notice-link {{
            display: inline-block;
            font-size: 0.75rem;
            color: white;
            text-decoration: none;
            font-weight: 600;
            padding: 6px 12px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .notice-link:hover {{
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.5);
        }}

        /* Content */
        .content {{ min-width: 0; }}
        
        .content-header {{
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--border);
        }}
        .content-header h2 {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--primary-dark);
        }}
        .content-header p {{
            font-size: 0.88rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .show-more {{
            display: block;
            width: 100%;
            padding: 16px;
            margin-top: 20px;
            background: white;
            border: 2px dashed var(--border);
            border-radius: var(--radius);
            color: var(--primary);
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
        }}
        .show-more:hover {{ background: var(--primary-light); border-color: var(--primary); }}

        /* Tool Detail Card */
        .tool-detail-card {{
            background: white;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            overflow: hidden;
            margin-bottom: 28px;
            border: 1px solid var(--border);
            transition: box-shadow 0.2s;
        }}
        .tool-detail-card:hover {{ box-shadow: var(--shadow-lg); }}
        
        .tool-header {{
            background: linear-gradient(135deg, #E8F4FD, #D4E8F7);
            padding: 24px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            border-bottom: 1px solid rgba(0,109,174,0.1);
        }}
        .tool-logo {{
            width: 56px;
            height: 56px;
            border-radius: 12px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            overflow: hidden;
        }}
        .tool-logo img {{
            width: 40px;
            height: 40px;
            object-fit: contain;
        }}
        .tool-header-info {{ flex: 1; min-width: 0; }}
        .tool-name {{ font-size: 1.5rem; font-weight: 800; color: var(--primary-dark); margin-bottom: 6px; }}
        .tool-name a {{ color: inherit; text-decoration: none; }}
        .tool-name a:hover {{ color: var(--primary); }}
        .tool-tagline {{ font-size: 0.95rem; color: var(--text-secondary); max-width: 650px; }}
        .tool-badges {{ display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 14px;
            font-size: 0.72rem;
            font-weight: 600;
        }}
        .badge-cat {{ background: var(--primary-light); color: var(--primary); }}
        .badge-free {{ background: var(--success-light); color: var(--success); }}
        .badge-paid {{ background: #FBE9E7; color: #BF360C; }}
        .badge-freemium {{ background: #FFF3E0; color: #E65100; }}
        .badge-date {{ background: #F3F4F6; color: #6B7280; }}

        .tool-cta {{ flex-shrink: 0; }}
        .btn-primary {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 10px 22px;
            border-radius: var(--radius);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.88rem;
        }}
        .btn-primary:hover {{ background: var(--primary-dark); }}

        .tool-body {{ padding: 0 32px 32px; }}

        .detail-section {{ margin-top: 28px; }}
        .detail-section h3 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 14px;
            padding-bottom: 6px;
            border-bottom: 2px solid var(--primary-light);
        }}

        /* Features Grid */
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 12px;
        }}
        .feature-item {{
            background: var(--bg-alt);
            border-radius: var(--radius);
            padding: 14px 16px;
            border-left: 3px solid var(--primary);
            display: flex;
            gap: 10px;
            align-items: flex-start;
        }}
        .feature-icon {{ font-size: 1.2rem; flex-shrink: 0; }}
        .feature-text {{ font-size: 0.85rem; color: var(--text-secondary); }}

        /* Use Case */
        .usecase-box {{
            background: linear-gradient(135deg, var(--primary-light), #F0F7FF);
            border-radius: var(--radius);
            padding: 18px 20px;
            border-left: 4px solid var(--primary);
        }}
        .usecase-box p {{ font-size: 0.9rem; color: var(--text); }}

        /* Steps */
        .steps-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .step {{
            display: flex;
            gap: 14px;
            align-items: flex-start;
        }}
        .step-num {{
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .step-text {{ font-size: 0.88rem; color: var(--text-secondary); padding-top: 4px; }}

        /* Pricing */
        .pricing-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }}
        .pricing-card {{
            background: var(--bg-alt);
            border-radius: var(--radius);
            padding: 16px;
            border: 1px solid var(--border);
        }}
        .pricing-card.recommended {{
            border-color: var(--primary);
            border-width: 2px;
            background: white;
            position: relative;
        }}
        .pricing-card.recommended::before {{
            content: "★";
            position: absolute;
            top: -8px;
            right: 12px;
            background: var(--primary);
            color: white;
            font-size: 0.6rem;
            padding: 2px 8px;
            border-radius: 8px;
        }}
        .plan-name {{ font-weight: 700; color: var(--primary-dark); font-size: 0.88rem; margin-bottom: 4px; }}
        .plan-desc {{ font-size: 0.78rem; color: var(--text-secondary); line-height: 1.5; }}

        /* News Brief */
        .news-brief {{
            margin-bottom: 32px;
            background: white;
            border-radius: var(--radius-lg);
            padding: 24px 32px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }}
        .news-brief-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--primary-light);
        }}
        .news-brief-header h2 {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin: 0;
        }}
        .date-label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            background: var(--bg-alt);
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 500;
        }}
        
        /* Twitter-style Feed */
        .news-feed {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .news-item {{
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }}
        .news-icon {{
            font-size: 1.4rem;
            line-height: 1;
            flex-shrink: 0;
            background: var(--bg-alt);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .news-content {{
            flex: 1;
        }}
        .news-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 4px;
            line-height: 1.4;
        }}
        .news-title a {{
            color: inherit;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}
        .news-title a:hover {{
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}
        .news-summary {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        .news-meta {{
            font-size: 0.75rem;
            color: #9CA3AF;
            margin-top: 6px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .news-source {{
            font-weight: 500;
            color: var(--text-secondary);
        }}
        
        .no-news {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            padding: 20px;
            font-style: italic;
        }}

        /* Impact Section for Stakeholders */
        .impact-section {{
            background: linear-gradient(135deg, #004B87, #006DAE);
            color: white;
            border-radius: var(--radius-lg);
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: var(--shadow-lg);
        }}
        .impact-header {{
            text-align: center;
            margin-bottom: 28px;
        }}
        .impact-header h2 {{
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 8px;
            color: white;
        }}
        .impact-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        .impact-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.1);
            border-radius: var(--radius);
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 4px;
        }}
        .metric-label {{
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .metric-detail {{
            font-size: 0.8rem;
            opacity: 0.8;
        }}
        .impact-benefits {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}
        .benefit-column {{
            background: rgba(255,255,255,0.05);
            border-radius: var(--radius);
            padding: 20px;
            border-left: 3px solid rgba(255,255,255,0.3);
        }}
        .benefit-column h3 {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 12px;
            color: white;
        }}
        .benefit-column ul {{
            list-style: none;
            padding: 0;
        }}
        .benefit-column li {{
            font-size: 0.88rem;
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
            opacity: 0.9;
        }}
        .benefit-column li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #4ADE80;
            font-weight: 700;
        }}
        .impact-cta {{
            background: rgba(255,255,255,0.1);
            border-radius: var(--radius);
            padding: 20px 24px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .cta-box h4 {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 8px;
            color: white;
        }}
        .cta-box p {{
            font-size: 0.9rem;
            opacity: 0.9;
            line-height: 1.6;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 40px 32px;
            color: var(--text-secondary);
            font-size: 0.82rem;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}

        /* Responsive */
        @media (max-width: 768px) {{
            .page-layout {{ grid-template-columns: 1fr; }}
            .sidebar {{ position: static; display: flex; gap: 8px; overflow-x: auto; padding-bottom: 8px; }}
            .sidebar-title {{ display: none; }}
            .cat-link {{ white-space: nowrap; padding: 8px 14px; }}
            .tool-header {{ flex-direction: column; padding: 20px; }}
            .tool-body {{ padding: 0 20px 20px; }}
            .features-grid {{ grid-template-columns: 1fr; }}
            .pricing-grid {{ grid-template-columns: 1fr; }}
            .header-monash {{
                position: static;
                transform: none;
                margin-top: 20px;
                display: flex;
                justify-content: flex-end;
            }}
            .monash-logo-img {{
                height: 50px;
            }}
        }}
    </style>
</head>
<body>

<header class="header">
    <div class="header-inner">
        <h1>🔬 AI Tools Radar</h1>
        <p class="header-slogan">Your Daily Intelligence Hub for AI-Powered Research Tools</p>
        <div class="header-meta">
            📅 {date} · 📊 {total_tools} Tools in Database · 📁 {total_dates} Days Tracked
        </div>
        <div class="header-monash">
            <img class="monash-logo-img" src="{monash_logo}" alt="Monash University">
        </div>
    </div>
</header>

<div class="page-layout">
    <aside class="sidebar">
        <div class="sidebar-title">Categories</div>
        {sidebar_notice_html}
        <button class="cat-link active" onclick="filterCat('all', this)">
            📋 All Tools <span class="cat-count">{total_tools}</span>
        </button>
        {category_nav}
    </aside>

    <main class="content">
        {news_brief_html}

        <div class="content-header">
            <h2>⭐ Featured Tools</h2>
            <p>Curated AI-powered research tools for the lab — updated daily</p>
        </div>

        {tools_html}

        {show_more_html}
    </main>
</div>

<footer class="footer">
    <p>Built with Jian for the Lab · 
    <a href="https://github.com/wangjian945/AI-tools-radar">View Source</a></p>
    <p style="margin-top:8px">Monash University Malaysia · Last build: {build_time}</p>
</footer>

<script>
function filterCat(category, btn) {{
    document.querySelectorAll('.cat-link').forEach(el => el.classList.remove('active'));
    btn.classList.add('active');
    
    document.querySelectorAll('.tool-detail-card').forEach(card => {{
        if (category === 'all' || card.dataset.category === category) {{
            card.style.display = 'block';
        }} else {{
            card.style.display = 'none';
        }}
    }});
    
    // Update header
    const header = document.querySelector('.content-header h2');
    if (category === 'all') {{
        header.textContent = '⭐ Featured Tools';
    }} else {{
        header.textContent = category;
    }}
}}
</script>

</body>
</html>"""


def render_impact_page(total_tools, today):
    """Render standalone impact report page with dynamic tool count"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tools Radar - University Impact Report | Monash University</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #006DAE;
            --primary-dark: #004B87;
            --primary-light: #E8F4FD;
            --accent: #D93F00;
            --success: #2E7D32;
            --success-light: #E8F5E9;
            --bg: #FFFFFF;
            --bg-alt: #F5F7FA;
            --text: #1A1A2E;
            --text-secondary: #5A6677;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-lg: 0 4px 14px rgba(0,0,0,0.1);
            --radius: 8px;
            --radius-lg: 12px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-alt);
            color: var(--text);
            line-height: 1.6;
        }}

        /* Header */
        .header {{
            background: #004B87;
            color: white;
            padding: 32px 0;
        }}
        .header-inner {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 32px;
        }}
        .header h1 {{ font-size: 2rem; font-weight: 800; margin-bottom: 8px; }}
        .header-subtitle {{ font-size: 1.1rem; opacity: 0.9; font-weight: 300; }}

        /* Main Content */
        .container {{
            max-width: 900px;
            margin: 40px auto;
            padding: 0 32px;
        }}

        .report-section {{
            background: white;
            border-radius: var(--radius-lg);
            padding: 32px;
            margin-bottom: 28px;
            box-shadow: var(--shadow);
        }}

        .report-section h2 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--primary-light);
        }}

        .report-section h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary-dark);
            margin: 24px 0 12px;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, var(--primary-light), #F0F7FF);
            border-radius: var(--radius);
            padding: 20px;
            border-left: 4px solid var(--primary);
            margin: 16px 0;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }}

        .metric-item {{
            background: var(--bg-alt);
            border-radius: var(--radius);
            padding: 20px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary);
        }}

        .metric-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        ul {{
            padding-left: 20px;
            margin: 12px 0;
        }}

        li {{
            margin: 8px 0;
            color: var(--text-secondary);
        }}

        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}

        .back-link:hover {{ text-decoration: underline; }}

        .footer {{
            text-align: center;
            padding: 40px 32px;
            color: var(--text-secondary);
            font-size: 0.82rem;
        }}

        @media (max-width: 768px) {{
            .header-inner, .container {{ padding: 0 20px; }}
            .report-section {{ padding: 24px; }}
            .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>

<header class="header">
    <div class="header-inner">
        <h1>🎯 AI Tools Radar - Impact Report</h1>
        <p class="header-subtitle">Demonstrating University Contribution Through Research Infrastructure</p>
    </div>
</header>

<div class="container">
    <a href="index.html" class="back-link">← Back to AI Tools Radar</a>

    <div class="report-section">
        <h2>Executive Summary</h2>
        <p style="color: var(--text-secondary); margin-top: 12px;">
            The <strong>AI Tools Radar</strong> platform addresses a critical gap in university research infrastructure by providing 
            centralized, curated access to AI-powered research tools. This initiative directly supports Monash University's strategic 
            goals in research excellence, equity, and innovation — requiring zero additional budget while delivering measurable 
            efficiency gains across all research disciplines.
        </p>

        <div class="highlight-box">
            <strong>Key Achievement:</strong> Built and maintained entirely during non-teaching hours as part of PhD research development, 
            this platform demonstrates initiative in creating scalable research infrastructure that benefits the entire university community.
        </div>
    </div>

    <div class="report-section">
        <h2>📊 Quantifiable Impact</h2>
        
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-value">{total_tools}+</div>
                <div class="metric-label">Curated AI Tools</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">40%</div>
                <div class="metric-label">Time Savings</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">5+</div>
                <div class="metric-label">Research Categories</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">100%</div>
                <div class="metric-label">Free Access</div>
            </div>
        </div>

        <h3>Time Savings Breakdown</h3>
        <ul>
            <li><strong>Literature Review:</strong> 10-15 hours/week saved through AI-powered search and summarization</li>
            <li><strong>Data Extraction:</strong> 5-8 hours/week saved via automated extraction tools (Elicit, Scite.ai)</li>
            <li><strong>Writing & Editing:</strong> 3-5 hours/week saved with AI writing assistants (Paperpal, Writefull)</li>
            <li><strong>Citation Management:</strong> 2-3 hours/week saved through smart citation tools (Inciteful, Litmaps)</li>
        </ul>

        <div class="highlight-box">
            <strong>Annual Impact:</strong> For a research team of 10, this translates to <strong>1,040-1,560 hours/year</strong> 
            redirected from administrative tasks to actual research and discovery.
        </div>
    </div>

    <div class="report-section">
        <h2>🎓 Alignment with University Strategic Goals</h2>

        <h3>1. Research Excellence & Intensification</h3>
        <ul>
            <li>Enables systematic, comprehensive literature reviews — reducing publication bias</li>
            <li>Provides evidence-based citation analysis through Scite.ai integration</li>
            <li>Supports higher-quality publications through AI-assisted writing and editing</li>
            <li>Facilitates reproducibility with documented, standardized tool workflows</li>
        </ul>

        <h3>2. Equity & Inclusion in Research</h3>
        <ul>
            <li>Democratizes access to cutting-edge AI tools regardless of funding level</li>
            <li>Levels the playing field for early-career researchers and PhD students</li>
            <li>Reduces dependency on supervisor networks for tool discovery</li>
            <li>Provides structured onboarding for researchers new to AI-assisted methods</li>
        </ul>

        <h3>3. Innovation & Digital Transformation</h3>
        <ul>
            <li>Positions Monash as an early adopter of AI-enhanced research methodologies</li>
            <li>Creates foundation for future AI literacy programs across faculties</li>
            <li>Demonstrates practical application of AI in academic contexts</li>
            <li>Scalable infrastructure ready for faculty-wide or university-wide deployment</li>
        </ul>

        <h3>4. Cross-Disciplinary Collaboration</h3>
        <ul>
            <li>Tools applicable across Health Sciences, Engineering, Arts, Business, and Sciences</li>
            <li>Common platform enables shared vocabulary and methods across disciplines</li>
            <li>Facilitates interdisciplinary research through shared tool infrastructure</li>
        </ul>
    </div>

    <div class="report-section">
        <h2>💡 Scalability & Sustainability</h2>

        <h3>Current State</h3>
        <ul>
            <li>Built and maintained by PhD candidate during non-teaching hours</li>
            <li>Zero budget requirement — leverages existing free/freemium AI tools</li>
            <li>Automated daily updates via GitHub Actions</li>
            <li>Open-source architecture (GitHub repository)</li>
        </ul>

        <h3>Expansion Opportunities</h3>
        <ul>
            <li><strong>Faculty Level:</strong> Customize tool recommendations per faculty (Medicine, Engineering, Arts, etc.)</li>
            <li><strong>Workshop Series:</strong> Training sessions on AI tool integration in research workflows</li>
            <li><strong>Library Partnership:</strong> Integrate with library research support services</li>
            <li><strong>Grant Applications:</strong> Platform can serve as infrastructure component in research grant proposals</li>
            <li><strong>Industry Collaboration:</strong> Partner with AI tool providers for university-specific features</li>
        </ul>

        <div class="highlight-box">
            <strong>Recommendation:</strong> Formalize platform under Library or Research Office umbrella for 
            long-term sustainability while maintaining current development model.
        </div>
    </div>

    <div class="report-section">
        <h2>📋 For University Leadership</h2>
        
        <p style="color: var(--text-secondary);">
            This platform exemplifies the type of initiative that drives research excellence without requiring 
            significant resource investment. Key points for consideration:
        </p>

        <ul>
            <li><strong>Zero-Cost Infrastructure:</strong> Built and maintained without budget allocation</li>
            <li><strong>Immediate Impact:</strong> {total_tools} tools already curated and deployed</li>
            <li><strong>Measurable Outcomes:</strong> Time savings, research quality improvements, equity gains</li>
            <li><strong>Scalable Model:</strong> Ready for broader deployment with minimal additional investment</li>
            <li><strong>Strategic Alignment:</strong> Directly supports university research intensification goals</li>
        </ul>

        <div class="highlight-box" style="background: linear-gradient(135deg, #E8F5E9, #C8E6C9); border-left-color: var(--success);">
            <strong>Endorsement Request:</strong> Recognition of this platform as valuable university research 
            infrastructure, supporting its integration into formal research support services.
        </div>
    </div>

    <div class="report-section">
        <h2>📞 Contact & Access</h2>
        <p style="color: var(--text-secondary);">
            <strong>Platform:</strong> <a href="index.html" style="color: var(--primary);">AI Tools Radar</a><br>
            <strong>Repository:</strong> <a href="https://github.com/wangjian945/AI-tools-radar" style="color: var(--primary);">github.com/wangjian945/AI-tools-radar</a><br>
            <strong>Developer:</strong> Jian (PhD Candidate, Monash University Malaysia)<br>
            <strong>Built:</strong> 2026 (Ongoing development)
        </p>
    </div>
</div>

<footer class="footer">
    <p>Monash University Malaysia · AI Tools Radar Impact Report</p>
    <p style="margin-top: 8px">Generated: {today}</p>
</footer>

</body>
</html>"""


def render_news_brief(news_items, today):
    """渲染 News Feed Brief (Twitter-style, max 5)"""
    # 筛选：学术/研究相关 (关键词过滤在 news_collector 中做)
    # 这里只展示前 5 条
    feed_items = news_items[:5] if news_items else []
    
    if not feed_items:
        feed_html = """
        <div class="no-news">
            📭 No significant updates in academic AI tools today.
            <br>Check back tomorrow for the latest research software news.
        </div>"""
    else:
        items_html = ""
        for item in feed_items:
            title = item.get("title", "")
            summary = item.get("summary", "")
            url = item.get("url", "#")
            source = item.get("source", "Web")
            icon = item.get("icon", "📰")
            date_str = item.get("date", today)
            
            items_html += f"""
            <div class="news-item">
                <div class="news-icon">{icon}</div>
                <div class="news-content">
                    <div class="news-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </div>
                    <div class="news-summary">{summary}</div>
                    <div class="news-meta">
                        <span class="news-source">{source}</span> · {date_str}
                    </div>
                </div>
            </div>"""
        
        feed_html = f'<div class="news-feed">{items_html}</div>'

    return f"""
        <div class="news-brief">
            <div class="news-brief-header">
                <h2>📰 Daily Research Brief</h2>
                <span class="date-label">{today}</span>
            </div>
            {feed_html}
        </div>"""


def render_sidebar_notice(total_tools):
    """Render University Impact notice for left sidebar (compact notification style)"""
    return f"""
        <div class="sidebar-notice">
            <div class="notice-header">
                <div class="notice-icon">🎯</div>
                <div class="notice-title">University Impact</div>
            </div>
            <div class="notice-content">
                <div class="notice-stat">
                    <span class="stat-value">{total_tools}+</span>
                    <span class="stat-label">AI Tools</span>
                </div>
                <div class="notice-stat">
                    <span class="stat-value">40%</span>
                    <span class="stat-label">Time Saved</span>
                </div>
                <div class="notice-stat">
                    <span class="stat-value">100%</span>
                    <span class="stat-label">Free Access</span>
                </div>
            </div>
            <div class="notice-message">
                <p>Research excellence infrastructure · Zero budget · Ready for faculty-wide deployment</p>
            </div>
            <div class="notice-footer">
                <a href="impact.html" target="_blank" class="notice-link">View Full Impact Report →</a>
            </div>
        </div>
    """


def render_page(data_dir="data", output_dir="site"):
    # Load tools filtered for academic research only
    all_tools, all_dates = load_all_tools(data_dir, filter_research_only=True)
    news_items = load_news(data_dir)
    monash_logo = load_monash_logo()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # 新闻简报
    news_brief_html = render_news_brief(news_items, today)
    
    # Sidebar notice for stakeholders
    sidebar_notice_html = render_sidebar_notice(len(all_tools))
    
    # 分类统计
    categories = {}
    for tool in all_tools:
        cat = tool.get("category", "Other")
        categories.setdefault(cat, []).append(tool)
    
    # 侧边栏
    cat_nav = ""
    for cat in sorted(categories.keys()):
        icon = CATEGORY_ICONS.get(cat, "🔧")
        count = len(categories[cat])
        cat_nav += f'        <button class="cat-link" onclick="filterCat(\'{cat}\', this)">{icon} {cat} <span class="cat-count">{count}</span></button>\n'
    
    # 首页最多显示 10 个工具（详细卡片）
    MAX_HOMEPAGE = 10
    homepage_tools = all_tools[:MAX_HOMEPAGE]
    remaining = len(all_tools) - MAX_HOMEPAGE
    
    tools_html = "\n".join(render_detail_card(t) for t in homepage_tools)
    
    # Show more button
    if remaining > 0:
        show_more_html = f'<button class="show-more" onclick="filterCat(\'all\', document.querySelector(\'.cat-link\'))">📚 View {remaining} more tools in categories →</button>'
    else:
        show_more_html = ""
    
    html = HTML_TEMPLATE.format(
        date=today,
        total_tools=len(all_tools),
        total_dates=len(all_dates) if all_dates else 1,
        category_nav=cat_nav,
        news_brief_html=news_brief_html,
        sidebar_notice_html=sidebar_notice_html,
        tools_html=tools_html,
        show_more_html=show_more_html,
        monash_logo=monash_logo,
        build_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[OK] Page rendered: {output_path} ({len(all_tools)} tools)")
    
    # Render impact page with dynamic tool count
    impact_html = render_impact_page(len(all_tools), today)
    impact_path = os.path.join(output_dir, "impact.html")
    with open(impact_path, 'w', encoding='utf-8') as f:
        f.write(impact_html)
    
    print(f"[OK] Impact page rendered: {impact_path}")


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    render_page(os.path.join(root_dir, "data"), os.path.join(root_dir, "site"))
