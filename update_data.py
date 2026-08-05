# -*- coding: utf-8 -*-
"""村驴菜谱 JSONL → recipes.js 转换脚本（含食材归一化）

用法:
    python update_data.py [recipe_db.jsonl路径]   # 从上游 JSONL 重新生成
    python enrich_data.py                          # 只给现有 recipes.js 补归一化字段

说明: 归一化(ings_norm)把食材变体合并为标准名（手枪鸡腿→鸡腿、五花肉馅→肉馅），
供网页"冰箱选材"功能做精确匹配。归一化规则见 norms.py（两脚本共用）。
"""
import json, os, collections, sys
import norms

# 用法: python update_data.py [recipe_db.jsonl路径]
# 默认从上游项目 clone 目录读取（../Cunlv-Skill/references/recipe_db.jsonl）
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, '..', 'Cunlv-Skill', 'references', 'recipe_db.jsonl')
DST = os.path.join(BASE, 'data', 'recipes.js')

recipes = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception as e:
            print("SKIP:", e)
            continue
        # 过滤广告和非菜谱
        if not r.get("is_recipe", True) or r.get("is_ad", False):
            continue
        recipes.append(r)

# 加 id + 归一化字段
for i, r in enumerate(recipes, 1):
    r["id"] = i
    r["_tags"] = r.get("tags", [])
    r["_ing"] = [x.get("name", "") for x in r.get("ingredients", [])]
    # 食材归一化（冰箱选材功能依赖）
    ings = []
    for x in r.get("ingredients", []):
        n = norms.norm(x.get("name", ""))
        if not norms.is_non_shop(x.get("name", "")) and not norms.is_non_shop(n):
            ings.append(n)
    seen = set()
    r["ings_norm"] = [i for i in ings if not (i in seen or seen.add(i))]

# 统计
print("总菜谱:", len(recipes))
all_tags = collections.Counter()
all_ing = collections.Counter()
for r in recipes:
    for t in r.get("tags", []):
        all_tags[t] += 1
    for x in r.get("ingredients", []):
        all_ing[x.get("name", "")] += 1
print("标签种类:", len(all_tags))
print("食材种类:", len(all_ing))
print("\nTop 30 标签:")
for t, c in all_tags.most_common(30):
    print(f"  {t}: {c}")

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8") as f:
    f.write("// 村驴菜谱库数据 (自动生成, 勿手改)\n")
    f.write("// 生成时间: 2026-08-05 (含食材归一化 ings_norm)\n")
    f.write("window.RECIPES = ")
    json.dump(recipes, f, ensure_ascii=False)
    f.write(";\n")
print("\n输出:", DST, os.path.getsize(DST), "bytes")
