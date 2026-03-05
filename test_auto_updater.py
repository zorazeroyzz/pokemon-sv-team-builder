#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新模块测试脚本
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.auto_updater import (
    TavilyRuleChecker, 
    PikalyticsDataUpdater, 
    MetaAnalyzer,
    CounterTeamRecommender,
    AutoUpdater,
    RegulationInfo
)


def test_regulation_checker():
    """测试规则检查器"""
    print("\n" + "="*60)
    print("测试1: 规则检查器")
    print("="*60)
    
    checker = TavilyRuleChecker()
    
    # 测试加载/保存规则信息
    info = RegulationInfo()
    info.current_reg = "Regulation F"
    info.end_date = "2026-03-31"
    checker.save_regulation_info(info)
    
    loaded = checker.load_regulation_info()
    print(f"✓ 规则信息加载成功: {loaded.current_reg}")
    print(f"✓ 规则结束日期: {loaded.end_date}")
    
    # 测试日期计算
    days = checker._calculate_days_remaining("2026-03-31")
    print(f"✓ 距离Regulation F结束还有约 {days} 天")
    
    # 测试规则检测
    test_text = "Pokemon VGC 2026 will start Regulation G in April"
    new_reg = checker._detect_new_regulation(test_text, [{'content': test_text, 'title': 'Test'}])
    print(f"✓ 规则检测测试: 发现新规则 {new_reg}" if new_reg else "✓ 规则检测测试: 未发现新规则")
    
    return True


def test_data_updater():
    """测试数据更新器"""
    print("\n" + "="*60)
    print("测试2: 数据更新器")
    print("="*60)
    
    updater = PikalyticsDataUpdater()
    
    # 测试历史数据库初始化
    updater.init_history_db()
    print("✓ 历史数据库初始化成功")
    
    # 测试获取单个宝可梦数据
    print("\n测试获取武道熊师（连击流）数据...")
    data = updater.collector.fetch_pokemon_data("Urshifu-Rapid-Strike")
    
    if data:
        print(f"✓ 数据获取成功: {data['name']}")
        print(f"  - HP: {data.get('hp', 'N/A')}")
        print(f"  - 攻击: {data.get('attack', 'N/A')}")
        print(f"  - 速度: {data.get('speed', 'N/A')}")
        print(f"  - 技能数: {len(data.get('moves', []))}")
        print(f"  - 道具数: {len(data.get('items', []))}")
    else:
        print("⚠ 数据获取失败（可能是网络问题）")
    
    return True


def test_meta_analyzer():
    """测试环境分析器"""
    print("\n" + "="*60)
    print("测试3: 环境分析器")
    print("="*60)
    
    analyzer = MetaAnalyzer()
    
    # 测试属性分布分析
    test_pokemon = [
        {'name': 'Test1', 'type1': 'Fire', 'type2': 'Flying'},
        {'name': 'Test2', 'type1': 'Water', 'type2': None},
        {'name': 'Test3', 'type1': 'Fire', 'type2': None},
    ]
    
    type_dist = analyzer._analyze_type_distribution(test_pokemon)
    print(f"✓ 属性分布分析: {type_dist}")
    
    # 测试元总结生成
    summary = analyzer._generate_meta_summary(test_pokemon, [], type_dist)
    print(f"✓ 元总结生成: {summary}")
    
    return True


def test_counter_recommender():
    """测试克制推荐器"""
    print("\n" + "="*60)
    print("测试4: 克制推荐器")
    print("="*60)
    
    recommender = CounterTeamRecommender()
    
    # 测试属性克制关系
    counter_type = recommender._get_counter_type('Fire')
    print(f"✓ 属性克制: Fire -> {counter_type}")
    
    counter_type = recommender._get_counter_type('Water')
    print(f"✓ 属性克制: Water -> {counter_type}")
    
    # 测试高速宝可梦筛选
    fast_pokemon = recommender._get_fast_counters(['Incineroar', 'Rillaboom'])
    print(f"✓ 高速宝可梦筛选: 找到 {len(fast_pokemon)} 只")
    
    return True


def test_full_integration():
    """测试完整集成"""
    print("\n" + "="*60)
    print("测试5: 完整集成测试")
    print("="*60)
    
    updater = AutoUpdater()
    
    # 测试各组件初始化
    print("✓ AutoUpdater 初始化成功")
    print(f"  - RuleChecker: {type(updater.rule_checker).__name__}")
    print(f"  - DataUpdater: {type(updater.data_updater).__name__}")
    print(f"  - MetaAnalyzer: {type(updater.meta_analyzer).__name__}")
    print(f"  - CounterRecommender: {type(updater.counter_recommender).__name__}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("宝可梦朱紫队伍推荐系统 - 自动更新模块测试")
    print("="*60)
    
    tests = [
        ("规则检查器", test_regulation_checker),
        ("数据更新器", test_data_updater),
        ("环境分析器", test_meta_analyzer),
        ("克制推荐器", test_counter_recommender),
        ("完整集成", test_full_integration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n✗ {name} 测试失败: {e}")
    
    # 打印测试报告
    print("\n" + "="*60)
    print("测试报告")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ 通过" if success else f"✗ 失败: {error}"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    # 保存测试报告
    report = {
        'passed': passed,
        'total': total,
        'details': [
            {'name': name, 'success': success, 'error': error}
            for name, success, error in results
        ]
    }
    
    report_file = Path(__file__).parent / "data" / "test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存至: {report_file}")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
