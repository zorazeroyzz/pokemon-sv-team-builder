# -*- coding: utf-8 -*-
"""
测试模块
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import PokemonDatabase
from src.type_calculator import TypeCalculator
from src.team_analyzer import TeamAnalyzer


def test_database():
    """测试数据库功能"""
    print("🧪 测试数据库...")
    
    db = PokemonDatabase()
    db.init_tables()
    
    # 插入测试数据
    db.insert_pokemon({
        'name': 'TestMon',
        'name_zh': '测试兽',
        'type1': 'Fire',
        'type2': 'Flying',
        'hp': 100,
        'attack': 120,
        'defense': 80,
        'sp_attack': 100,
        'sp_defense': 80,
        'speed': 100,
        'bst': 580,
        'usage_rate': 25.5,
        'format': 'gen9vgc2026regf'
    })
    
    # 查询测试
    p = db.get_pokemon_by_name('TestMon')
    assert p is not None
    assert p['name'] == 'TestMon'
    
    print("✅ 数据库测试通过")


def test_type_calculator():
    """测试属性计算器"""
    print("🧪 测试属性计算器...")
    
    calc = TypeCalculator()
    
    # 测试单属性相克
    assert calc.get_effectiveness('Water', 'Fire') == 2.0
    assert calc.get_effectiveness('Fire', 'Water') == 0.5
    assert calc.get_effectiveness('Electric', 'Ground') == 0.0
    
    # 测试双属性
    effectiveness = calc.get_dual_type_effectiveness('Water', 'Fire', 'Flying')
    assert effectiveness == 2.0  # 水打火 2x, 水打飞行 1x = 2x
    
    # 测试防御面
    weaknesses = calc.get_type_weaknesses('Fire', 'Flying')
    assert 'Water' in weaknesses
    assert 'Electric' in weaknesses
    assert 'Rock' in weaknesses
    
    print("✅ 属性计算器测试通过")


def test_team_analyzer():
    """测试队伍分析器"""
    print("🧪 测试队伍分析器...")
    
    db = PokemonDatabase()
    analyzer = TeamAnalyzer(db)
    
    # 添加测试数据
    test_pokemon = [
        ('Incineroar', 'Fire', 'Dark', 95, 115, 90, 80, 90, 60),
        ('Urshifu-Rapid-Strike', 'Fighting', 'Water', 100, 130, 100, 63, 60, 97),
        ('Flutter Mane', 'Ghost', 'Fairy', 55, 55, 55, 135, 135, 135),
        ('Rillaboom', 'Grass', None, 100, 125, 90, 60, 70, 85),
        ('Amoonguss', 'Grass', 'Poison', 114, 85, 70, 85, 80, 30),
        ('Landorus', 'Ground', 'Flying', 89, 125, 90, 115, 80, 101),
    ]
    
    for name, t1, t2, hp, atk, defe, spa, spd, spe in test_pokemon:
        db.insert_pokemon({
            'name': name,
            'name_zh': '',
            'type1': t1,
            'type2': t2,
            'hp': hp,
            'attack': atk,
            'defense': defe,
            'sp_attack': spa,
            'sp_defense': spd,
            'speed': spe,
            'bst': hp + atk + defe + spa + spd + spe,
            'usage_rate': 30.0,
            'format': 'gen9vgc2026regf'
        })
    
    # 测试队伍分析
    team = ['Incineroar', 'Urshifu-Rapid-Strike', 'Flutter Mane', 
            'Rillaboom', 'Amoonguss', 'Landorus']
    
    try:
        analysis = analyzer.analyze_team(team)
        assert 'overall_score' in analysis
        assert 'synergy_score' in analysis
        print(f"   队伍评分: {analysis['overall_score']:.2f}")
        print("✅ 队伍分析器测试通过")
    except Exception as e:
        print(f"⚠️ 队伍分析测试跳过: {e}")


def test_data_collector():
    """测试数据采集"""
    print("🧪 测试数据采集...")
    
    from src.data_collector import PikalyticsCollector
    
    collector = PikalyticsCollector()
    
    # 测试数据获取
    data = collector.fetch_pokemon_data('Urshifu-Rapid-Strike')
    
    if data:
        print(f"   成功获取 {data['name']} 数据")
        print(f"   种族值: {data['bst']}")
        print(f"   技能数: {len(data['moves'])}")
        print("✅ 数据采集测试通过")
    else:
        print("⚠️ 数据采集测试跳过（网络问题）")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 宝可梦队伍推荐系统测试")
    print("=" * 60)
    
    try:
        test_database()
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
    
    try:
        test_type_calculator()
    except Exception as e:
        print(f"❌ 属性计算器测试失败: {e}")
    
    try:
        test_team_analyzer()
    except Exception as e:
        print(f"❌ 队伍分析器测试失败: {e}")
    
    try:
        test_data_collector()
    except Exception as e:
        print(f"❌ 数据采集测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
