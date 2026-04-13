"""
AI Tools Radar - 完整流水线
一键运行：采集工具 → 采集新闻 → LLM 处理 → 渲染页面
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from collector import fetch_daily_tools, save_raw_data
from processor import process_all_tools
from news_collector import collect_daily_news
from renderer import render_page


def run_pipeline():
    data_dir = os.path.join(ROOT_DIR, "data")
    site_dir = os.path.join(ROOT_DIR, "site")
    
    print("=" * 60)
    print("🚀 AI Tools Radar - Daily Pipeline")
    print("=" * 60)
    
    # Step 1: 采集工具
    print("\n📡 STEP 1/4: Collecting tools...")
    tools = fetch_daily_tools()
    raw_path = save_raw_data(tools, data_dir)
    
    # Step 2: 采集新闻
    print("\n📰 STEP 2/4: Collecting AI news...")
    collect_daily_news(data_dir)
    
    # Step 3: LLM 处理
    if tools:
        print("\n🤖 STEP 3/4: Processing with LLM...")
        processed_path = process_all_tools(raw_path, data_dir)
    else:
        print("\n⚠️ STEP 3/4: No new tools, skipping LLM processing.")
    
    # Step 4: 渲染 HTML（即使没有新工具也要渲染，因为有新闻）
    print("\n🎨 STEP 4/4: Rendering HTML page...")
    render_page(data_dir, site_dir)
    
    print("\n" + "=" * 60)
    print("✅ Pipeline complete!")
    print(f"   📄 Output: {os.path.join(site_dir, 'index.html')}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
