p = r'h:\2026AIC·算法创新赛\源码_restored\scripts\_gen_ppt3.py'
c = open(p, encoding='utf-8').read()

# 把截图占位页里画虚线的循环（那个 for dy in range...）简化掉
# 找到那段，去掉
import re

old_dashed = '''    # 大虚线占位（用多个矩形模拟）
    for dy in range(0, int(Inches(4.8)), 8):
        R(s, Inches(0.6), Inches(1.9) + dy, Inches(12.1), Pt(2), C_LINE)'''

new_dashed = '''    # 占位边框
    R(s, Inches(0.6), Inches(1.9), Inches(12.1), Inches(4.8), RGBColor(0xEE,0xF2,0xF5), C_LINE)'''

c = c.replace(old_dashed, new_dashed)
print('dashed loop simplified')

open(p, 'w', encoding='utf-8').write(c)
print('done')
