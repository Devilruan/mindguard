import sqlite3, json, re

conn = sqlite3.connect(r'h:\2026AIC·算法创新赛\源码_restored\mmhs.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM screening_sessions')
total = c.fetchone()[0]

c.execute('SELECT risk_level, COUNT(*) FROM screening_sessions GROUP BY risk_level')
levels = dict(c.fetchall())

c.execute('SELECT AVG(phq9_total), AVG(gad7_total), AVG(risk_score) FROM screening_sessions')
avgs = c.fetchone()

c.execute("SELECT COUNT(*) FROM screening_sessions WHERE crisis_level='CRISIS'")
crisis = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM interventions')
interv = c.fetchone()[0]

print("=== 数据库统计 ===")
print(f"总会话数: {total}")
print(f"风险等级分布: {levels}")
print(f"平均 PHQ-9: {round(avgs[0],1)}")
print(f"平均 GAD-7: {round(avgs[1],1)}")
print(f"平均风险分: {round(avgs[2],1)}")
print(f"CRISIS 级: {crisis}")
print(f"干预工单: {interv}")

# 抓 settings.py 的危机词库
with open(r'h:\2026AIC·算法创新赛\源码_restored\config\settings.py', encoding='utf-8') as f:
    s = f.read()
kw_n = len(re.findall(r'"([^"]{2,20})"', re.search(r"CRISIS_KEYWORDS\s*=\s*\{(.+?)\n\}", s, re.DOTALL).group(1)))
kb_n = len(re.findall(r'^    ', re.search(r"MENTAL_HEALTH_KB\s*=\s*\{(.+?)\n\}", s, re.DOTALL).group(1), re.MULTILINE))
print(f"\n=== 配置 ===")
print(f"危机关键词总数: {kw_n}")

# engine.py 行数
with open(r'h:\2026AIC·算法创新赛\源码_restored\backend\core\neuro_symbolic\engine.py', encoding='utf-8') as f:
    lines = f.readlines()
print(f"engine.py 行数: {len(lines)}")

# 各 API 行数
import os
api_dir = r'h:\2026AIC·算法创新赛\源码_restored\backend\api'
for fn in os.listdir(api_dir):
    if fn.endswith('.py'):
        with open(os.path.join(api_dir, fn), encoding='utf-8') as f:
            print(f"  api/{fn}: {len(f.readlines())} 行")

conn.close()
