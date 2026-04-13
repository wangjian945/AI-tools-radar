import base64

# 官方 Monash Blue: #004B87
# 使用简洁的 SVG 版本（盾牌 + 文字）
svg_logo = '''<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
  <g fill="#FFFFFF">
    <path d="M60 10 L140 10 L140 70 L60 110 L60 10 Z" stroke="#FFFFFF" stroke-width="3" fill="none"/>
    <rect x="75" y="25" width="20" height="15" fill="#FFFFFF"/>
    <line x1="85" y1="25" x2="85" y2="40" stroke="#004B87" stroke-width="1"/>
    <polygon points="100,55 103,62 110,62 105,67 107,74 100,70 93,74 95,67 90,62 97,62" fill="#FFFFFF"/>
    <text x="160" y="55" font-family="Georgia, serif" font-size="42" font-weight="bold" fill="#FFFFFF">MONASH</text>
    <text x="160" y="90" font-family="Arial, sans-serif" font-size="28" fill="#FFFFFF">University</text>
  </g>
</svg>'''

b64 = base64.b64encode(svg_logo.encode('utf-8')).decode('utf-8')
result = 'data:image/svg+xml;base64,' + b64

with open('monash_logo_embedded.txt', 'w') as f:
    f.write(result)

print('Saved to monash_logo_embedded.txt')
print('Length:', len(result), 'chars')
