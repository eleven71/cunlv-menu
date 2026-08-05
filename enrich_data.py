# -*- coding: utf-8 -*-
"""数据增强：为每道菜的食材添加归一化名称(norm)，供冰箱选材功能匹配使用
用法: python enrich_data.py
归一化规则见 norms.py（与 update_data.py 共用）
"""
import json, os
import norms

# 脚本位于项目根目录，数据文件用相对路径（兼容任意 clone 位置）
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'recipes.js')

with open(SRC, encoding='utf-8') as f:
    content = f.read()
data = json.loads(content[content.index('['):content.rindex(']')+1])

n_added = 0
for r in data:
    ings = []
    for x in r.get('ingredients', []):
        raw = x.get('name', '')
        n = norms.norm(raw)
        if not norms.is_non_shop(raw) and not norms.is_non_shop(n):
            ings.append(n)
    # 去重保序
    seen = set()
    ings = [i for i in ings if not (i in seen or seen.add(i))]
    r['ings_norm'] = ings
    n_added += len(ings)

with open(SRC, 'w', encoding='utf-8') as f:
    f.write('// 村驴菜谱库数据 (自动生成, 勿手改)\n')
    f.write('// 生成时间: 2026-08-05 (含食材归一化 ings_norm)\n')
    f.write('window.RECIPES = ')
    json.dump(data, f, ensure_ascii=False)
    f.write(';\n')

print(f"菜谱: {len(data)} 道, 归一化食材条目: {n_added}")
print("文件大小:", os.path.getsize(SRC), "bytes")
# 验证
r = [x for x in data if x['dish_name']=='醋蒸鸡'][0]
print("醋蒸鸡 ings_norm:", r['ings_norm'])
