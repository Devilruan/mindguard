import sqlite3, os, re

db = r'h:\2026AIC·算法创新赛\源码_restored\mmhs.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# schema
c.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for r in c.fetchall():
    if r[0]:
        print(r[0])
print("---")

# 行数
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for (tn,) in c.fetchall():
    c.execute(f'SELECT COUNT(*) FROM {tn}')
    print(f'{tn}: {c.fetchone()[0]} rows')
print("---")

# 看 sessions 的列
c.execute("PRAGMA table_info(screening_sessions)")
cols = [r[1] for r in c.fetchall()]
print("screening_sessions columns:", cols)

# 第一行数据
c.execute("SELECT * FROM screening_sessions LIMIT 1")
row = c.fetchone()
for col, val in zip(cols, row):
    print(f"  {col} = {repr(val)[:80]}")

conn.close()
