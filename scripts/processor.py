"""
AI Tools Processor
使用 LLM 对采集的工具进行分类、摘要、生成结构化数据
支持 Gemini API、EasyClaw 或 OpenAI API
"""

import json
import os
import sys
import time
from datetime import datetime


def call_llm(prompt, system_prompt="You are a helpful assistant.", max_retries=3):
    """
    统一 LLM 调用接口
    优先使用 Gemini API（云端友好），备选 EasyClaw/OpenAI
    """
    # 方式 1: Gemini API (Google) - 云端运行首选
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        return _call_gemini(prompt, system_prompt, gemini_key, max_retries)
    
    # 方式 2: EasyClaw API (通过本地端口)
    easyclaw_port = os.environ.get("EASYCLAW_PORT", "3457")
    easyclaw_token = os.environ.get("EASYCLAW_TOKEN", "")
    
    if easyclaw_token:
        return _call_easyclaw(prompt, system_prompt, easyclaw_port, easyclaw_token, max_retries)
    
    # 方式 3: OpenAI API
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        return _call_openai(prompt, system_prompt, openai_key, max_retries)
    
    # 方式 4: 无 LLM 可用，用简单规则处理
    print("  [WARN] No LLM available, using rule-based processing")
    return _rule_based_process(prompt)


def _call_gemini(prompt, system_prompt, api_key, max_retries=3):
    """通过 Google Gemini API 调用"""
    try:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }
        
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=60) as client:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 429:
                        time.sleep(2 ** attempt)
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise e
    except ImportError:
        raise RuntimeError("httpx is required. Run: pip install httpx")


def _call_easyclaw(prompt, system_prompt, port, token, max_retries=3):
    """通过 EasyClaw 本地 API 调用 LLM"""
    try:
        import httpx
        url = f"http://127.0.0.1:{port}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "default",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=60) as client:
                    resp = client.post(url, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise e
    except ImportError:
        import urllib.request
        url = f"http://127.0.0.1:{port}/v1/chat/completions"
        payload = json.dumps({
            "model": "default",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data["choices"][0]["message"]["content"]


def _call_openai(prompt, system_prompt, api_key, max_retries=3):
    """通过 OpenAI API 调用"""
    try:
        import httpx
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=60) as client:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 429:
                        retry_after = int(resp.headers.get("Retry-After", 5))
                        time.sleep(retry_after)
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise e
    except ImportError:
        raise RuntimeError("httpx is required for OpenAI API calls. Run: pip install httpx")


def _rule_based_process(prompt):
    """无 LLM 时的降级规则处理"""
    return json.dumps({
        "name": "Unknown Tool",
        "category": "Other",
        "one_liner": "No LLM available for processing",
        "key_features": [],
        "use_case": "N/A",
        "pricing": "Unknown",
        "quality_score": 3
    })


# ============================================================
# 工具处理逻辑
# ============================================================

SYSTEM_PROMPT = """You are an AI research tools analyst for a university research lab.
Your job is to evaluate and categorize AI-powered tools for academic researchers.
Always respond with valid JSON only, no markdown formatting."""

PROCESS_PROMPT_TEMPLATE = """Analyze the following AI tool and generate a structured summary.

Tool Information:
- Name: {name}
- Source: {source}
- Description: {description}
- URL: {url}
{extra_info}

Respond with ONLY valid JSON (no markdown code blocks):
{{
  "name": "<tool name>",
  "category": "<one of: Literature Review, Data Analysis, Writing & Drafting, Visualization, Peer Review, Coding & Dev, Experiment Design, Other>",
  "one_liner": "<one sentence summary, max 25 words, in English>",
  "key_features": ["<feature 1>", "<feature 2>", "<feature 3>"],
  "use_case": "<specific scenario for academic researchers, 1-2 sentences, in English>",
  "pricing": "<Free / Freemium / Paid / Open Source>",
  "quality_score": <1-10, based on relevance to academic research>,
  "is_research_relevant": <true/false, is this actually useful for academic research?>
}}"""


def process_single_tool(tool):
    """处理单个工具，返回结构化数据"""
    extra_info = ""
    if tool.get("stars"):
        extra_info += f"- GitHub Stars: {tool['stars']}\n"
    if tool.get("language"):
        extra_info += f"- Language: {tool['language']}\n"
    if tool.get("topics"):
        extra_info += f"- Topics: {', '.join(tool['topics'][:5])}\n"
    
    prompt = PROCESS_PROMPT_TEMPLATE.format(
        name=tool.get("name", "Unknown"),
        source=tool.get("source", "Unknown"),
        description=(tool.get("description", "") or "")[:500],
        url=tool.get("url", ""),
        extra_info=extra_info
    )
    
    try:
        result_text = call_llm(prompt, SYSTEM_PROMPT)
        
        # 清理可能的 markdown 代码块标记
        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1] if "\n" in result_text else result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        result["url"] = tool.get("url", "")
        result["source"] = tool.get("source", "")
        result["stars"] = tool.get("stars", 0)
        result["collected_date"] = datetime.utcnow().strftime('%Y-%m-%d')
        return result
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON parse error for {tool.get('name', '?')}: {e}")
        return {
            "name": tool.get("name", "Unknown"),
            "category": "Other",
            "one_liner": (tool.get("description", "") or "")[:100],
            "key_features": [],
            "use_case": "",
            "pricing": "Unknown",
            "quality_score": 3,
            "is_research_relevant": True,
            "url": tool.get("url", ""),
            "source": tool.get("source", ""),
            "stars": tool.get("stars", 0),
            "collected_date": datetime.utcnow().strftime('%Y-%m-%d')
        }
    except Exception as e:
        print(f"  [ERROR] Processing {tool.get('name', '?')}: {e}")
        return None


def process_all_tools(raw_data_path, output_dir="data"):
    """
    批量处理所有工具
    """
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    tools = raw_data.get("tools", [])
    print(f"\n🤖 Processing {len(tools)} tools with LLM...")
    
    processed = []
    for i, tool in enumerate(tools):
        print(f"  [{i+1}/{len(tools)}] {tool.get('name', '?')[:40]}...")
        result = process_single_tool(tool)
        if result:
            processed.append(result)
        # 控制调用频率
        if i < len(tools) - 1:
            time.sleep(1)
    
    # 过滤：只保留与科研相关、质量分 >= 5 的工具
    filtered = [t for t in processed if t.get("is_research_relevant", True) and t.get("quality_score", 0) >= 5]
    filtered.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    
    # 保存处理后的数据
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"processed_{date_str}.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": date_str,
            "processed_at": datetime.utcnow().isoformat(),
            "total_collected": len(tools),
            "total_processed": len(processed),
            "total_qualified": len(filtered),
            "tools": filtered
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Processed: {len(processed)} | Qualified: {len(filtered)}")
    print(f"💾 Saved to {output_path}")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 自动查找最新的 raw 文件
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        raw_files = sorted([f for f in os.listdir(data_dir) if f.startswith("raw_")])
        if not raw_files:
            print("❌ No raw data files found. Run collector.py first.")
            sys.exit(1)
        raw_path = os.path.join(data_dir, raw_files[-1])
    else:
        raw_path = sys.argv[1]
    
    process_all_tools(raw_path)
