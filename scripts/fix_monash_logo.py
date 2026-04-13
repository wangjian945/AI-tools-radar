import re

# 读取 renderer.py
with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\scripts\renderer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换硬编码的 SVG logo 为 {monash_logo} 占位符
old_pattern = r'<img class="monash-logo-img" src="data:image/svg\+xml;base64,[A-Za-z0-9+/=]+" alt="Monash University">'
new_tag = '<img class="monash-logo-img" src="{monash_logo}" alt="Monash University">'

content = re.sub(old_pattern, new_tag, content)

# 保存
with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\scripts\renderer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed monash_logo placeholder in renderer.py')
