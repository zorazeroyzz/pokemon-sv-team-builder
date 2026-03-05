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


if __name__ == '__main__':
    main()
