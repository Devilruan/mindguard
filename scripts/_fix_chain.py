p = r'h:\2026AIC·算法创新赛\源码_restored\scripts\_gen_ppt.py'
c = open(p, encoding='utf-8').read()

fixes = [
    (
        '    ("          → R003 激活，优先级 6，文本抑郁风险权重 +0.25",    C_TEAL),',
        '    ("", "          → R003 激活，优先级 6，文本抑郁风险权重 +0.25",    C_TEAL),'
    ),
    (
        '    ("          → 自杀风险权重 +0.30",                              C_TEAL),',
        '    ("", "          → 自杀风险权重 +0.30",                              C_TEAL),'
    ),
    (
        '    ("          → R006 激活，焦虑交叉验证 +0.20",                  C_TEAL),',
        '    ("", "          → R006 激活，焦虑交叉验证 +0.20",                  C_TEAL),'
    ),
]
for old, new in fixes:
    if old in c:
        c = c.replace(old, new)
        print(f'fixed: {old[:40]}...')
    else:
        print(f'NOT FOUND: {old[:40]}...')

open(p, 'w', encoding='utf-8').write(c)
print('done')
