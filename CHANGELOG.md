# Changelog

所有项目的显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.1.0] - 2026-03-06

### ✨ 新增功能

- **队伍推荐系统** - 全新的AI队伍推荐功能
  - 支持4种策略：平衡队、进攻队、防守队、戏法空间队
  - 基于VGC 2026 Regulation F规则的热门配置
  - 包含技能、道具、性格、EV分配的完整配置
  - 中文本地化支持（宝可梦名、技能名、道具名、性格）

- **REST API服务器** (`api_server.py`)
  - `/api/recommend` - 获取推荐队伍
  - `/api/analyze` - 分析队伍配置
  - `/api/strategies` - 获取可用策略列表
  - 支持CORS跨域访问

- **可视化推荐界面** (`public/recommender.html`)
  - 响应式网页设计
  - 策略选择按钮
  - 宝可梦卡片展示（含种族值条形图）
  - 类型徽章显示

### 🔧 技术改进

- 重构项目结构，新增 `src/recommender/` 模块
- 添加 `pokemon_names_zh.py` 中文映射文件
- 集成类型相克计算算法
- 支持从SQLite数据库动态查询宝可梦数据

### 📁 新增文件

```
pokemon-sv-team-builder/
├── api_server.py                 # REST API服务器
├── src/
│   └── recommender/
│       ├── pokemon_recommender.py   # 推荐核心算法
│       └── pokemon_names_zh.py      # 中文本地化
└── public/
    └── recommender.html          # 可视化界面
```

## [1.0.0] - 2026-03-05

### ✨ 初始版本

- **VGC图鉴展示** - 完整的宝可梦朱紫图鉴
  - 1025只全国图鉴
  - 413只朱紫可用宝可梦
  - PKHeX官方立绘

- **数据库支持**
  - SQLite数据库 (`data/pokemon.db`)
  - 宝可梦基础数据（种族值、属性、技能）
  - 道具数据表
  - 技能数据表

- **数据抓取脚本**
  - `expand_pokedex.py` - 从PokeAPI获取帕底亚图鉴数据
  - `scrape_pikalytics.py` - 抓取Pikalytics使用率数据
  - `download_all_sprites.py` - 下载PKHeX立绘资源

- **可视化展示**
  - `index.html` - 主展示页面
  - 版本答案推荐图
  - 完整推荐阵容图
  - 全国图鉴大图

- **基础服务器**
  - `server.py` - 简单的HTTP服务器
  - 支持图片路径重定向

[Unreleased]: https://github.com/zorazeroyzz/pokemon-sv-team-builder/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/zorazeroyzz/pokemon-sv-team-builder/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/zorazeroyzz/pokemon-sv-team-builder/releases/tag/v1.0.0
