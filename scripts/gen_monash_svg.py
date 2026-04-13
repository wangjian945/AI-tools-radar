import base64

# 官方 Monash Blue: #004B87
# 创建符合品牌规范的 SVG logo（盾牌 + 文字）
svg_logo = '''<svg viewBox="0 0 500 150" xmlns="http://www.w3.org/2000/svg">
  <g fill="#FFFFFF">
    <!-- 盾牌轮廓 -->
    <path d="M50 20 L150 20 L150 90 L50 140 L50 20 Z" stroke="#FFFFFF" stroke-width="4" fill="none"/>
    <!-- 打开的书 -->
    <path d="M70 40 L90 40 L90 55 L70 55 Z" fill="#FFFFFF"/>
    <line x1="80" y1="40" x2="80" y2="55" stroke="#004B87" stroke-width="2"/>
    <!-- 剑与月桂花环 -->
    <circle cx="115" cy="47" r="8" stroke="#FFFFFF" stroke-width="2" fill="none"/>
    <line x1="115" y1="42" x2="115" y2="52" stroke="#FFFFFF" stroke-width="2"/>
    <!-- 南十字星 -->
    <polygon points="85,100 88,106 95,106 90,111 92,118 85,114 78,118 80,111 75,106 82,106" fill="#FFFFFF"/>
    <!-- 文字 -->
    <text x="170" y="75" font-family="Georgia, serif" font-size="55" font-weight="bold" fill="#FFFFFF">MONASH</text>
    <text x="170" y="115" font-family="Arial, sans-serif" font-size="32" fill="#FFFFFF">University</text>
  </g>
</svg>'''

b64 = base64.b64encode(svg_logo.encode('utf-8')).decode('utf-8')
result = 'data:image/svg+xml;base64,' + b64

with open(r'C:\Users\wangj\.easyclaw\workspace\ai-tools-radar\monash_logo_embedded.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print('Saved. Length:', len(result))
