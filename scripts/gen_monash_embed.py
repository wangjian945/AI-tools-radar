import base64
import json

# 读取 logo PNG
with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\monash_logo.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

result = 'data:image/png;base64,' + b64

# 保存为 JSON 文件（方便 renderer 读取）
with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\monash_logo_data.json', 'w', encoding='utf-8') as f:
    json.dump({'logo': result}, f)

print('✅ Saved monash_logo_data.json')
print('   Length:', len(result), 'chars')
print('   Size:', round(len(b64)/1024, 1), 'KB')
