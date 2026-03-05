# 宝可梦朱紫队伍推荐系统

## 项目结构

```
pokemon-sv-team-builder/
├── data/
│   ├── pokemon.db          # SQLite数据库
│   └── type_chart.json     # 属性相克表
├── src/
│   ├── __init__.py
│   ├── database.py         # 数据库操作
│   ├── data_collector.py   # 数据采集
│   ├── type_calculator.py  # 属性计算
│   ├── team_analyzer.py    # 队伍分析
│   ├── ai_engine.py        # AI推荐引擎
│   └── cli.py              # 命令行接口
├── tests/
│   └── test_team_builder.py
├── requirements.txt
└── main.py                 # 主入口
```

## 功能特性

1. **数据采集**: 从 Pikalytics 获取 VGC2025/2026 数据
2. **数据库存储**: SQLite 存储宝可梦、技能、道具、队伍数据
3. **属性计算**: 完整的属性相克矩阵、联防分析
4. **AI 引擎**: LongCat 本地筛选 + Kimi 2.5 深度推荐
5. **用户接口**: 命令行交互，支持多种队伍风格

## 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python main.py --init-db

# 采集数据
python main.py --collect-data

# 生成队伍推荐
python main.py --recommend --style balanced
```

## 队伍风格

- `balanced`: 平衡型
- `offensive`: 进攻型
- `defensive`: 防守型
