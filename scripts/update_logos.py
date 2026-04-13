import json

with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\data\processed_2026-03-28.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 为已知工具硬编码 logo URL（多源 fallback，Google 服务最可靠放第一位）
logo_map = {
    'Elicit': ['https://www.google.com/s2/favicons?domain=elicit.com&sz=256', 'https://elicit.com/apple-touch-icon.png', 'https://elicit.com/favicon.ico'],
    'Consensus': ['https://www.google.com/s2/favicons?domain=consensus.app&sz=256', 'https://consensus.app/apple-touch-icon.png', 'https://consensus.app/favicon.ico'],
    'Connected Papers': ['https://www.connectedpapers.com/favicon.ico', 'https://logo.clearbit.com/connectedpapers.com'],
    'ResearchRabbit': ['https://www.researchrabbit.ai/favicon.ico', 'https://logo.clearbit.com/researchrabbit.ai'],
    'Semantic Scholar': ['https://www.semanticscholar.org/favicon.ico', 'https://logo.clearbit.com/semanticscholar.org'],
    'Scite': ['https://scite.ai/favicon.ico', 'https://logo.clearbit.com/scite.ai'],
    'NotebookLM': ['https://notebooklm.google.com/favicon.ico', 'https://www.google.com/s2/favicons?domain=notebooklm.google.com&sz=256'],
    'ChatPDF': ['https://www.chatpdf.com/favicon.ico', 'https://logo.clearbit.com/chatpdf.com'],
    'SciSpace': ['https://typeset.io/favicon.ico', 'https://logo.clearbit.com/typeset.io'],
    'Zotero': ['https://www.zotero.org/favicon.ico', 'https://logo.clearbit.com/zotero.org'],
    'Mendeley': ['https://www.mendeley.com/favicon.ico', 'https://logo.clearbit.com/mendeley.com'],
    'Perplexity AI': ['https://www.perplexity.ai/favicon.ico', 'https://logo.clearbit.com/perplexity.ai'],
    'Jenni AI': ['https://jenni.ai/favicon.ico', 'https://logo.clearbit.com/jenni.ai'],
    'Grammarly': ['https://www.grammarly.com/favicon.ico', 'https://logo.clearbit.com/grammarly.com'],
    'Overleaf': ['https://www.overleaf.com/favicon.ico', 'https://logo.clearbit.com/overleaf.com'],
    'Litmaps': ['https://www.litmaps.com/favicon.ico', 'https://logo.clearbit.com/litmaps.com'],
    'Scholarcy': ['https://www.scholarcy.com/favicon.ico', 'https://logo.clearbit.com/scholarcy.com'],
    'Research Buddy': ['https://researchbuddy.app/favicon.ico', 'https://logo.clearbit.com/researchbuddy.app'],
    'QuillBot': ['https://quillbot.com/favicon.ico', 'https://logo.clearbit.com/quillbot.com'],
}

for tool in data['tools']:
    name = tool['name']
    if name in logo_map:
        tool['logos'] = logo_map[name]
    else:
        domain = tool.get('url', '').replace('https://', '').replace('http://', '').split('/')[0]
        tool['logos'] = [f'https://www.google.com/s2/favicons?domain={domain}&sz=256']

with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\data\processed_2026-03-28.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('✅ Updated logo URLs for', len(data['tools']), 'tools')
