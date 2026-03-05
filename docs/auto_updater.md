# 宝可梦朱紫队伍推荐系统 - 自动更新模块

## 功能概述

自动更新模块提供以下功能：

1. **规则监控** - 使用 Tavily API 每天检查 VGC 规则是否更新
2. **数据更新** - 从 Pikalytics 抓取最新使用率数据
3. **环境分析** - 分析当前环境热门队伍、核心组合
4. **克制推荐** - 基于环境数据，推荐克制当前热门的队伍

## 模块结构

```
src/
├── auto_updater.py          # 自动更新主模块
    ├── TavilyRuleChecker       # 规则检查器
    ├── PikalyticsDataUpdater   # 数据更新器
    ├── MetaAnalyzer            # 环境分析器
    ├── CounterTeamRecommender  # 克制推荐器
    └── AutoUpdater             # 主控类
```

## 使用方法

### 1. 运行完整自动更新

```bash
python main.py --auto-update
```

这将执行以下流程：
1. 检查 VGC 规则是否有更新
2. 从 Pikalytics 更新数据（前30只热门宝可梦）
3. 分析当前环境（热门宝可梦、核心组合、属性分布）
4. 生成克制队伍推荐

### 2. 查看环境分析

```bash
python main.py --meta
```

显示内容：
- 当前热门宝可梦 TOP 10
- 热门核心组合
- 属性分布统计
- 上升趋势宝可梦

### 3. 查看克制推荐

```bash
python main.py --counter
```

显示内容：
- 当前环境主要威胁
- 推荐克制队伍（3种策略）
- AI 战术分析

### 4. 作为模块调用

```python
from src.auto_updater import AutoUpdater

updater = AutoUpdater()
results = updater.run_full_update()
```

## 数据存储

### 历史数据库 (`data/usage_history.db`)

包含以下表：
- `usage_history` - 使用率历史记录
- `meta_snapshot` - 环境分析快照

### 规则信息 (`data/regulation_info.json`)

存储当前 VGC 规则信息：
- 当前规则名称
- 开始/结束日期
- 最后检查时间

### 克制推荐 (`data/counter_recommendations.json`)

存储最近10次克制推荐结果

## 技术实现

### 规则监控
- 使用 Tavily API 搜索最新 VGC 规则信息
- 自动检测 Regulation F/G/H 等新规则
- 计算规则剩余天数，提前预警

### 数据更新
- 从 Pikalytics API 获取数据
- 更新 SQLite 数据库
- 记录历史使用率变化

### 环境分析
- 统计热门宝可梦排名
- 分析核心组合（基于队友关联）
- 属性分布统计
- 趋势分析（对比7天前数据）

### 克制推荐
- 分析热门威胁的属性弱点
- 生成3种策略的克制队伍：
  1. 反热门属性特化队
  2. 综合反制队
  3. 高速压制队
- 使用 Kimi 2.5 AI 生成战术分析

## 测试

运行测试脚本：

```bash
python test_auto_updater.py
```

测试内容：
- 规则检查器功能
- 数据更新器功能
- 环境分析器功能
- 克制推荐器功能
- 完整集成测试

## 定时任务配置

建议配置 cron 任务每天运行：

```bash
# 每天凌晨3点运行自动更新
0 3 * * * cd /root/pokemon-sv-team-builder && python3 main.py --auto-update >> /var/log/pokemon-updater.log 2>&1
```

## API 密钥配置

模块使用以下 API 密钥（已内置）：
- Tavily API: `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`
- Kimi API: `sk-kimi-TMzmu8ann5Q4DhnRRyY9Vkd22dSgkLivrjmejRIcIGp7kqT6Z9lIp22jvU9hYmjJ`

也可通过环境变量自定义：
```bash
export TAVILY_API_KEY="your-key"
export KIMI_API_KEY="your-key"
export KIMI_BASE_URL="https://api.moonshot.cn/v1"
```
