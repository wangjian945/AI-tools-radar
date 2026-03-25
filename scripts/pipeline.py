"""
AI Tools Radar - 完整流水线
一键运行：采集 → 处理 → 渲染
"""

import os
import sys

# 确保路径正确
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from collector import fetch_daily_tools, save_raw_data
from processor import process_all_tools
from renderer import render_page


def run_pipeline():
    """执行完整流水线"""
    data_dir = os.path.join(ROOT_DIR, "data")
    site_dir = os.path.join(ROOT_DIR, "site")
    
    print("=" * 60)
    print("🚀 AI Tools Radar - Daily Pipeline")
    print("=" * 60)
    
    # Step 1: 采集
    print("\n📡 STEP 1/3: Collecting tools...")
    tools = fetch_daily_tools()
    raw_path = save_raw_data(tools, data_dir)
    
    if not tools:
        print("⚠️ No tools collected today. Skipping processing.")
        return
    
    # Step 2: LLM 处理
    print("\n🤖 STEP 2/3: Processing with LLM...")
    processed_path = process_all_tools(raw_path, data_dir)
    
    # Step 3: 渲染 HTML
    print("\n🎨 STEP 3/3: Rendering HTML page...")
    render_page(processed_path, site_dir)
    
    print("\n" + "=" * 60)
    print("✅ Pipeline complete!")
    print(f"   📄 Output: {os.path.join(site_dir, 'index.html')}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
