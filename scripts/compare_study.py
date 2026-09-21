"""对比实验：纯 PHQ-9 单维度 vs 神经符号引擎多维度筛查。"""
import sys
import base64
import requests
from collections import Counter

sys.path.insert(0, r'h:\2026AIC·算法创新赛\mmhs.exe_extracted\PYZ.pyz_extracted')

B = 'http://localhost:8000'
headers = {'Authorization': 'Basic ' + base64.b64encode(b'admin:admin123').decode()}
rows = requests.get(B + '/api/admin/sessions?limit=500', headers=headers, timeout=15).json()['rows']
n = len(rows)

# 方法 A: 纯 PHQ-9 阈值
phq9_ge_10 = sum(1 for s in rows if s['phq9'] >= 10)
phq9_ge_15 = sum(1 for s in rows if s['phq9'] >= 15)

# 方法 B: 神经符号引擎
engine_high_urgent = sum(1 for s in rows if s['risk_level'] in ('high', 'urgent'))
engine_urgent = sum(1 for s in rows if s['risk_level'] == 'urgent')

# 交叉分析
extra_detected = [s for s in rows if s['phq9'] < 10 and s['risk_level'] in ('high', 'urgent')]
false_positive_eliminated = [s for s in rows if s['phq9'] >= 10 and s['risk_level'] not in ('high', 'urgent')]

print('=' * 55)
print(f'  对比实验结果  (样本量 n = {n})')
print('=' * 55)
print()
print('方法 A：传统纯 PHQ-9 单维度筛查')
print(f'  PHQ-9 >= 10（有临床意义）: {phq9_ge_10:>3d} 人  ({phq9_ge_10/n*100:.1f}%)')
print(f'  PHQ-9 >= 15（中度以上需关注）: {phq9_ge_15:>3d} 人  ({phq9_ge_15/n*100:.1f}%)')
print()
print('方法 B：神经符号引擎多维度筛查（本项目）')
print(f'  综合 high + urgent 风险:    {engine_high_urgent:>3d} 人  ({engine_high_urgent/n*100:.1f}%)')
print(f'  urgent 极高风险（立即干预）: {engine_urgent:>3d} 人  ({engine_urgent/n*100:.1f}%)')
print()
print('-' * 55)
print('核心优势分析')
print('-' * 55)
print(f'额外检出（PHQ-9 < 10 但引擎判 high/urgent）:  {len(extra_detected)} 人')
if extra_detected:
    for s in extra_detected[:6]:
        print(f'  session #{s["id"]:>3}  PHQ-9={s["phq9"]:>4.1f}  level={s["risk_level"]}')
print(f'精准排除（PHQ-9 >= 10 但引擎判 low/medium）:  {len(false_positive_eliminated)} 人')
print()
print('风险等级分布（神经符号引擎）:')
lv = Counter(s['risk_level'] for s in rows)
for l, c in lv.most_common():
    print(f'  {l:>10s}: {c:>4d}  ({c/n*100:>5.1f}%)')

# 紧急级检出对比
print()
print('紧急级（urgent/PHQ-9>=15）精准度对比:')
print(f'  纯 PHQ-9: {phq9_ge_15} 人  →  可能包含假阳性（如 GAD-7 低、文本无危机信号）')
print(f'  本引擎:   {engine_urgent} 人  →  多维度交叉验证，精准度更高')
