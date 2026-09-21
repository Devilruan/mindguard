p = r'h:\2026AIC·算法创新赛\源码_restored\scripts\_gen_ppt3.py'
c = open(p, encoding='utf-8').read()

fixes = [
    ("    '  LLM 温柔话术 + RAG 行动步骤', C_SEC, False),",
     "    ('  LLM 温柔话术 + RAG 行动步骤', C_SEC, False),"),
    ("    '  RAG 建议 + 模板温柔话术（降级）', C_SEC, False),",
     "    ('  RAG 建议 + 模板温柔话术（降级）', C_SEC, False),"),
]

for old, new in fixes:
    if old in c:
        c = c.replace(old, new)
        print(f'fixed: {old[:40]}...')
    else:
        print(f'NOT FOUND: {old[:40]}...')

open(p, 'w', encoding='utf-8').write(c)
print('done')
