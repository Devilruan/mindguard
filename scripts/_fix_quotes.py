p = r'h:\2026AIC·算法创新赛\源码_restored\scripts\_gen_ppt.py'
c = open(p, encoding='utf-8').read()

# 问题行：把  ('          '  替换成  ('          "
# 实际上问题是  ('          '→  这种写法，应该是  ('          "→
old1 = "    ('          '→ R003 激活，优先级 6，文本抑郁风险权重 +0.25',    C_TEAL),"
new1 = '    ("          → R003 激活，优先级 6，文本抑郁风险权重 +0.25",    C_TEAL),'
old2 = "    ('          '→ 自杀风险权重 +0.30',                              C_TEAL),"
new2 = '    ("          → 自杀风险权重 +0.30",                              C_TEAL),'
old3 = "    ('          '→ R006 激活，焦虑交叉验证 +0.20',                  C_TEAL),"
new3 = '    ("          → R006 激活，焦虑交叉验证 +0.20",                  C_TEAL),'

c = c.replace(old1, new1).replace(old2, new2).replace(old3, new3)
open(p, 'w', encoding='utf-8').write(c)
print('fixed')
