# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 命令行接口
"""
import argparse
import sys
import json
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.database import PokemonDatabase
from src.data_collector import PikalyticsCollector, POKEMON_NAME_ZH
from src.type_calculator import TypeCalculator
from src.team_analyzer import TeamAnalyzer
from src.ai_engine import AIEngine
from src.default_sets import get_pokemon_set, ITEM_NAME_ZH, MOVE_NAME_ZH, NATURE_NAME_ZH


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_team_recommendation(recommendation: dict, style: str):
    """打印队伍推荐结果"""
    print_header(f"🎮 推荐队伍 ({style}型)")
    
    if 'error' in recommendation and recommendation['error']:
        print(f"\n❌ 错误: {recommendation['error']}")
        return
    
    team = recommendation.get('team', [])
    members = recommendation.get('members', [])
    
    if not team:
        print("\n⚠️ 未能生成队伍推荐")
        return
    
    # 打印队伍成员
    print("\n📋 队伍成员:")
    print("-" * 60)
    
    for i, member in enumerate(members, 1):
        name = member.get('name', team[i-1] if i-1 < len(team) else 'Unknown')
        name_zh = POKEMON_NAME_ZH.get(name, '')
        
        # 获取默认配置
        default_set = get_pokemon_set(name)
        
        print(f"\n{i}. {name} {f'({name_zh})' if name_zh else ''}")
        print(f"   角色: {default_set.get('role', member.get('role', '未知'))}")
        
        # 道具
        item = member.get('item', '')
        if not item or item == '待定':
            items = default_set.get('items', ['待定'])
            item = items[0] if items else '待定'
        print(f"   道具: {item}")
        
        # 性格
        nature = member.get('nature', '')
        if not nature or nature == '待定':
            natures = default_set.get('natures', ['根据build选择'])
            nature = natures[0] if natures else '根据build选择'
        print(f"   性格: {nature}")
        
        # 配招
        moves = member.get('moves', [])
        if not moves or moves[0] in ['根据对战环境选择', '待配置']:
            moves = default_set.get('moves', ['根据环境选择'])
        print(f"   配招: {' / '.join(moves[:4])}")
    
    # 打印战术思路
    print("\n" + "-" * 60)
    print("\n📖 战术思路:")
    print(recommendation.get('strategy', '暂无'))
    
    if 'tips' in recommendation:
        print("\n💡 对战要点:")
        print(recommendation['tips'])
    
    if 'note' in recommendation:
        print(f"\n⚠️ 注意: {recommendation['note']}")


def init_database():
    """初始化数据库"""
    print_header("🗄️ 初始化数据库")
    db = PokemonDatabase()
    db.init_tables()
    print("✅ 数据库初始化完成！")


def collect_data():
    """采集数据"""
    print_header("📊 数据采集")
    
    db = PokemonDatabase()
    collector = PikalyticsCollector()
    
    # 采集前30只热门宝可梦
    collector.collect_all_data(db, limit=30)
    
    print("\n✅ 数据采集完成！")


def recommend_team(style: str = 'balanced', use_ai: bool = True):
    """生成队伍推荐"""
    print_header(f"🎯 生成队伍推荐 (风格: {style})")
    
    # 初始化组件
    db = PokemonDatabase()
    type_calc = TypeCalculator()
    analyzer = TeamAnalyzer(db)
    
    # 生成候选队伍
    print("\n🔧 生成候选队伍...")
    candidates = analyzer.generate_team_candidates(style=style)
    print(f"✅ 生成 {len(candidates)} 个候选队伍")
    
    if use_ai:
        # 使用 AI 引擎
        ai_engine = AIEngine(db, type_calc)
        recommendation = ai_engine.recommend_team(candidates, style)
    else:
        # 仅使用本地分析
        print("\n🔍 本地分析中...")
        best_team = None
        best_score = -1
        
        for team in candidates[:20]:
            try:
                analysis = analyzer.analyze_team(team)
                score = analyzer.score_team_for_style(analysis, style)
                if score > best_score:
                    best_score = score
                    best_team = analysis
            except:
                continue
        
        if best_team:
            recommendation = {
                'team': best_team['team'],
                'members': [{'name': name, 'role': '待配置'} for name in best_team['team']],
                'strategy': f'{style}型队伍，基于属性相克和热门宝可梦组合分析',
                'note': '本地分析模式（未使用AI）'
            }
        else:
            recommendation = {'error': '未能找到合适的队伍'}
    
    # 打印结果
    print_team_recommendation(recommendation, style)
    
    # 保存结果
    output_path = Path(__file__).parent / "data" / f"recommended_team_{style}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendation, f, ensure_ascii=False, indent=2)
    print(f"\n💾 推荐结果已保存至: {output_path}")


def analyze_existing_team(team_str: str):
    """分析已有队伍"""
    print_header("🔍 队伍分析")
    
    team = [name.strip() for name in team_str.split(',')]
    
    if len(team) != 6:
        print(f"❌ 错误: 队伍必须包含6只宝可梦，当前 {len(team)} 只")
        return
    
    db = PokemonDatabase()
    analyzer = TeamAnalyzer(db)
    
    try:
        analysis = analyzer.analyze_team(team)
        
        print(f"\n📋 队伍: {', '.join(team)}")
        print("-" * 60)
        
        print(f"\n📊 综合评分: {analysis['overall_score']:.2f}/10")
        print(f"🔗 协同评分: {analysis['synergy_score']:.2f}")
        print(f"🔥 热门度: {analysis['popularity_score']:.1f}%")
        
        print(f"\n📈 种族值统计:")
        stats = analysis['bst_stats']
        print(f"   平均BST: {stats['avg_bst']:.0f}")
        print(f"   平均攻击: {stats['avg_attack']:.0f}")
        print(f"   平均特攻: {stats['avg_sp_attack']:.0f}")
        print(f"   平均防御: {stats['avg_defense']:.0f}")
        print(f"   平均特防: {stats['avg_sp_defense']:.0f}")
        print(f"   平均速度: {stats['avg_speed']:.0f}")
        
        print(f"\n🛡️ 防御分析:")
        defense = analysis['defensive_analysis']
        if defense.get('weaknesses'):
            print(f"   弱点属性: {', '.join(w['type'] for w in defense['weaknesses'][:5])}")
        if defense.get('resistances'):
            print(f"   抗性属性: {', '.join(r['type'] for r in defense['resistances'][:5])}")
        
        print(f"\n⚔️ 攻击覆盖:")
        offense = analysis['offensive_analysis']
        print(f"   覆盖评分: {offense['coverage_score']:.2f}")
        print(f"   效果拔群: {len(offense['super_effective'])} 种属性")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def run_auto_update():
    """运行自动更新"""
    from src.auto_updater import AutoUpdater
    
    updater = AutoUpdater()
    results = updater.run_full_update()
    
    # 保存结果
    output_file = Path(__file__).parent / "data" / "last_update_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("自动更新结果摘要")
    print("=" * 60)
    
    if 'regulation_check' in results and results['regulation_check']:
        print(f"📋 规则检查: {results['regulation_check'].get('message', 'N/A')}")
    
    if 'data_update' in results and results['data_update']:
        if 'updated' in results['data_update']:
            print(f"📊 数据更新: {results['data_update']['updated']} 成功, {results['data_update'].get('failed', 0)} 失败")
        else:
            print(f"📊 数据更新: {results['data_update'].get('error', '未知状态')}")
    
    if 'meta_analysis' in results and results['meta_analysis']:
        print(f"🔍 环境分析: {results['meta_analysis'].get('summary', 'N/A')}")
    
    if 'counter_recommendation' in results and results['counter_recommendation']:
        teams_count = results['counter_recommendation'].get('teams_generated', 0)
        print(f"⚔️ 克制推荐: {teams_count} 支队伍已生成")
    
    print(f"\n💾 详细结果已保存至: {output_file}")


def show_meta_analysis():
    """显示当前环境分析"""
    from src.auto_updater import MetaAnalyzer
    
    print_header("🔍 当前环境分析")
    
    analyzer = MetaAnalyzer()
    analysis = analyzer.analyze_current_meta()
    
    print(f"\n📅 分析时间: {analysis['date']}")
    print(f"🎮 对战规则: {analysis['format']}")
    print(f"\n📊 环境总结: {analysis['summary']}")
    
    print("\n🏆 热门宝可梦 TOP 10:")
    for i, p in enumerate(analysis['top_pokemon'][:10], 1):
        name_zh = p.get('name_zh', '')
        name_display = f"{p['name']} ({name_zh})" if name_zh else p['name']
        print(f"   {i:2d}. {name_display}")
    
    print("\n🔗 热门核心组合:")
    for combo in analysis['core_combinations'][:5]:
        members_zh = combo.get('members_zh', [])
        members_str = ' + '.join([f"{m} ({zh})" if zh else m 
                                  for m, zh in zip(combo['members'], members_zh)])
        print(f"   • {members_str}")
    
    print("\n🔥 热门属性分布:")
    for type_name, count in list(analysis['type_distribution'].items())[:5]:
        print(f"   • {type_name}: {count} 只")
    
    if 'trends' in analysis and 'rising' in analysis['trends']:
        print("\n📈 上升趋势:")
        for item in analysis['trends']['rising'][:5]:
            name_zh = POKEMON_NAME_ZH.get(item['name'], '')
            name_display = f"{item['name']} ({name_zh})" if name_zh else item['name']
            print(f"   • {name_display}: +{item['change']:.1f}%")


def show_counter_teams():
    """显示克制队伍推荐"""
    from src.auto_updater import MetaAnalyzer, CounterTeamRecommender
    
    print_header("⚔️ 克制队伍推荐")
    
    # 先获取环境分析
    analyzer = MetaAnalyzer()
    meta_analysis = analyzer.analyze_current_meta()
    
    # 生成克制推荐
    recommender = CounterTeamRecommender()
    result = recommender.generate_counter_teams(meta_analysis)
    
    print(f"\n🎯 目标环境: {result['target_meta']}")
    
    print("\n⚠️ 主要威胁:")
    for threat in result['threats_analyzed'][:5]:
        name_zh = threat.get('name_zh', '')
        name_display = f"{threat['name']} ({name_zh})" if name_zh else threat['name']
        weaknesses = ', '.join(threat['weaknesses'][:3]) if threat['weaknesses'] else 'N/A'
        print(f"   • {name_display} - 弱点: {weaknesses}")
    
    print("\n🛡️ 推荐克制队伍:")
    for i, team in enumerate(result['recommended_counter_teams'], 1):
        print(f"\n   {i}. {team['name']}")
        print(f"      策略: {team['strategy']}")
        print(f"      目标: {team['target']}")
        print(f"      成员: {', '.join(team['members_zh'])}")
    
    if result.get('ai_analysis') and result['ai_analysis'].get('status') == 'success':
        print("\n🤖 AI 战术分析:")
        print(result['ai_analysis']['analysis'])


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='宝可梦朱紫队伍推荐系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --init-db                    # 初始化数据库
  python main.py --collect-data               # 采集数据
  python main.py --recommend --style balanced # 生成平衡型队伍
  python main.py --analyze "Incineroar,Urshifu-Rapid-Strike,Flutter Mane,Rillaboom,Amoonguss,Landorus"
  python main.py --auto-update                # 运行完整自动更新
  python main.py --meta                       # 显示环境分析
  python main.py --counter                    # 显示克制推荐
        """
    )
    
    parser.add_argument('--init-db', action='store_true',
                        help='初始化数据库')
    parser.add_argument('--collect-data', action='store_true',
                        help='从 Pikalytics 采集数据')
    parser.add_argument('--recommend', action='store_true',
                        help='生成队伍推荐')
    parser.add_argument('--style', choices=['balanced', 'offensive', 'defensive'],
                        default='balanced',
                        help='队伍风格 (默认: balanced)')
    parser.add_argument('--analyze', type=str,
                        help='分析已有队伍（逗号分隔6只宝可梦名称）')
    parser.add_argument('--no-ai', action='store_true',
                        help='不使用 AI 推荐（仅本地分析）')
    parser.add_argument('--auto-update', action='store_true',
                        help='运行自动更新（规则检查、数据更新、环境分析、克制推荐）')
    parser.add_argument('--meta', action='store_true',
                        help='显示当前环境分析')
    parser.add_argument('--counter', action='store_true',
                        help='显示克制队伍推荐')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # 执行命令
    if args.init_db:
        init_database()
    
    if args.collect_data:
        collect_data()
    
    if args.recommend:
        recommend_team(args.style, use_ai=not args.no_ai)
    
    if args.analyze:
        analyze_existing_team(args.analyze)
    
    if args.auto_update:
        run_auto_update()
    
    if args.meta:
        show_meta_analysis()
    
    if args.counter:
        show_counter_teams()


if __name__ == '__main__':
    main()
