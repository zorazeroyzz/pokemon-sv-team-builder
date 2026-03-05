# 宝可梦朱紫队伍推荐系统 - 数据库扩展报告

## 扩展概况

- **原数据库规模**: 30只宝可梦
- **扩展后规模**: 413只宝可梦
- **扩展数量**: +383只宝可梦
- **数据来源**: PokeAPI (Paldea Pokedex)

## 数据统计

### 宝可梦分布
- **总数**: 413只
- **技能数**: 263个
- **宝可梦-技能关联**: 8,173条

### 属性分布 (Top 10)
1. 水 (Water): 45只
2. 一般 (Normal): 45只
3. 草 (Grass): 38只
4. 电 (Electric): 35只
5. 龙 (Dragon): 27只
6. 恶 (Dark): 26只
7. 虫 (Bug): 25只
8. 岩石 (Rock): 20只
9. 超能力 (Psychic): 20只
10. 幽灵 (Ghost): 20只

### 高BST宝可梦 (Top 10)
1. 请假王 (Slaking) - BST 670
2. 故勒顿 (Koraidon) - BST 670
3. 密勒顿 (Miraidon) - BST 670
4. 海豚侠-全能形态 (Palafin-Hero) - BST 650
5. 烈咬陆鲨 (Garchomp) - BST 600
6. 黏美龙 (Goodra) - BST 600
7. 暴飞龙 (Salamence) - BST 600
8. 多龙巴鲁托 (Dragapult) - BST 600
9. 班基拉斯 (Tyranitar) - BST 600
10. 快龙 (Dragonite) - BST 600

## 新增内容

### 1. 朱紫新宝可梦 (Gen 9)
- 新叶喵、呆火鳄、润水鸭等御三家进化链
- 雄伟牙、吼叫尾、猛恶菇等悖谬宝可梦
- 古简蜗、古剑豹、古鼎鹿、古玉鱼四灾兽
- 故勒顿、密勒顿封面神
- 厄诡椪、太乐巴戈斯等传说宝可梦

### 2. 前代宝可梦
- 第一世代: 妙蛙种子、小火龙、杰尼龟等
- 第二世代: 菊草叶、火球鼠、小锯鳄等
- 第三世代: 木守宫、火稚鸡、水跃鱼等
- 第四世代: 草苗龟、小火焰猴、波加曼等
- 第五世代: 藤藤蛇、暖暖猪、水水獭等

### 3. 特殊形态
- 飘香豚 (雄/雌)
- 一家鼠 (四只家庭)
- 鬃岩狼人 (白昼/黑夜/黄昏)
- 花舞鸟 (四种风格)
- 怒鹦哥 (四种羽色)
- 野蛮鲈鱼 (三种条纹)
- 土龙节节 (两节/三节)
- 颤弦蝾螈 (高调/低调)
- 超能艳鸵 (两种形态)
- 米立龙 (三种花纹)
- 海豚侠 (平凡/全能)

## 数据库结构

### 表结构
1. **pokemon** - 宝可梦基础信息
   - name, name_zh, type1, type2
   - hp, attack, defense, sp_attack, sp_defense, speed, bst
   - usage_rate, format

2. **moves** - 技能信息
   - name, name_zh, type, category
   - power, accuracy, pp, description

3. **pokemon_moves** - 宝可梦-技能关联
   - pokemon_name, move_name, usage_rate, format

4. **items** - 道具信息
   - name, name_zh, description, category

5. **pokemon_items** - 宝可梦-道具关联
   - pokemon_name, item_name, usage_rate, format

6. **pokemon_teammates** - 宝可梦-队友关联
   - pokemon_name, teammate_name, synergy_rate, format

7. **recommended_teams** - 推荐队伍
   - team_name, style, pokemon_list, strategy

## 文件更新

### 新增文件
- `data/pokemon.db` - 扩展后的数据库文件
- `src/default_sets_expanded.py` - 扩展的默认配招数据

### 配招数据
包含约80只热门宝可梦的推荐配招、道具、性格配置，涵盖:
- VGC 2026 Regulation F 热门宝可梦
- 朱紫新宝可梦
- 经典强力宝可梦

## 使用方法

```python
from src.database import PokemonDatabase

db = PokemonDatabase()

# 获取所有宝可梦
all_pokemon = db.get_all_pokemon()

# 获取特定宝可梦
pokemon = db.get_pokemon_by_name("koraidon")

# 获取宝可梦技能
moves = db.get_pokemon_moves("koraidon")
```

## 数据验证

- ✅ 所有宝可梦都有完整的种族值数据
- ✅ 所有宝可梦都有属性信息
- ✅ 技能数据已关联
- ✅ 数据库完整性检查通过

## GitHub推送

- 仓库: https://github.com/zorazeroyzz/pokemon-sv-team-builder
- 分支: master
- 提交: 扩展数据库至413只宝可梦 - 全图鉴数据

## 后续建议

1. 更新 `main.py` 以支持新的数据库结构
2. 添加更多默认配招数据
3. 实现队伍推荐算法优化
4. 添加更多中文翻译
5. 集成使用率数据
