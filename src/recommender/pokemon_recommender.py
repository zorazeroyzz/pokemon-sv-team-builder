# -*- coding: utf-8 -*-
"""
宝可梦VGC队伍推荐系统
基于Pikalytics数据和类型互补算法
"""

import requests
import sqlite3
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# 导入中文名映射
from pokemon_names_zh import POKEMON_NAMES_ZH, MOVE_NAMES_ZH, ITEM_NAMES_ZH, NATURES_ZH

@dataclass
class Pokemon:
    name: str
    name_zh: str
    types: List[str]
    stats: Dict[str, int]
    bst: int
    usage_rate: float = 0.0
    
    @property
    def type1(self) -> str:
        return self.types[0] if self.types else 'normal'
    
    @property
    def type2(self) -> Optional[str]:
        return self.types[1] if len(self.types) > 1 else None

@dataclass
class TeamSlot:
    pokemon: Pokemon
    moves: List[str]
    item: str
    ability: str
    nature: str
    evs: Dict[str, int]
    
    def to_dict(self) -> Dict:
        return {
            'name': self.pokemon.name,
            'name_zh': self.pokemon.name_zh,
            'types': self.pokemon.types,
            'types_zh': [self._get_type_zh(t) for t in self.pokemon.types],
            'stats': self.pokemon.stats,
            'bst': self.pokemon.bst,
            'moves': self.moves,
            'moves_zh': [MOVE_NAMES_ZH.get(m, m) for m in self.moves],
            'item': self.item,
            'item_zh': ITEM_NAMES_ZH.get(self.item, self.item),
            'ability': self.ability,
            'nature': self.nature,
            'nature_zh': NATURES_ZH.get(self.nature, self.nature),
            'evs': self.evs
        }
    
    def _get_type_zh(self, type_en: str) -> str:
        type_map = {
            'normal': '一般', 'fire': '火', 'water': '水', 'electric': '电',
            'grass': '草', 'ice': '冰', 'fighting': '格斗', 'poison': '毒',
            'ground': '地面', 'flying': '飞行', 'psychic': '超能力', 'bug': '虫',
            'rock': '岩石', 'ghost': '幽灵', 'dragon': '龙', 'dark': '恶',
            'steel': '钢', 'fairy': '妖精'
        }
        return type_map.get(type_en, type_en)

class PokemonRecommender:
    def __init__(self, db_path: str = "data/pokemon.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # 类型相克表
        self.type_chart = self._load_type_chart()
        
        # VGC热门配置
        self.vgc_sets = self._load_vgc_sets()
        
    def _load_type_chart(self) -> Dict[str, Dict[str, float]]:
        """加载类型相克表"""
        return {
            'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
            'fire': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'dragon': 0.5, 'steel': 2},
            'water': {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
            'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
            'grass': {'fire': 0.5, 'water': 2, 'grass': 0.5, 'poison': 0.5, 'ground': 2, 'flying': 0.5, 'bug': 0.5, 'rock': 2, 'dragon': 0.5, 'steel': 0.5},
            'ice': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 0.5, 'ground': 2, 'flying': 2, 'dragon': 2, 'steel': 0.5},
            'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock': 2, 'ghost': 0, 'dark': 2, 'steel': 2, 'fairy': 0.5},
            'poison': {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0, 'fairy': 2},
            'ground': {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock': 2, 'steel': 2},
            'flying': {'electric': 0.5, 'grass': 2, 'fighting': 2, 'bug': 2, 'rock': 0.5, 'steel': 0.5},
            'psychic': {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'dark': 0, 'steel': 0.5},
            'bug': {'fire': 0.5, 'grass': 2, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark': 2, 'steel': 0.5, 'fairy': 0.5},
            'rock': {'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'flying': 2, 'bug': 2, 'steel': 0.5},
            'ghost': {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
            'dragon': {'dragon': 2, 'steel': 0.5, 'fairy': 0},
            'dark': {'fighting': 0.5, 'psychic': 2, 'ghost': 2, 'dark': 0.5, 'fairy': 0.5},
            'steel': {'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2, 'rock': 2, 'steel': 0.5, 'fairy': 2},
            'fairy': {'fire': 0.5, 'fighting': 2, 'poison': 0.5, 'dragon': 2, 'dark': 2, 'steel': 0.5}
        }
    
    def _load_vgc_sets(self) -> Dict[str, Dict]:
        """加载VGC热门配置（基于Regulation F）"""
        return {
            'flutter-mane': {
                'role': 'special-sweeper',
                'tier': 'S',
                'moves': ['moonblast', 'shadow-ball', 'power-gem', 'icy-wind'],
                'items': ['focus-sash', 'life-orb', 'booster-energy'],
                'natures': ['timid', 'modest'],
                'evs': {'hp': 0, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 4, 'speed': 252}
            },
            'iron-hands': {
                'role': 'physical-tank',
                'tier': 'S',
                'moves': ['fake-out', 'drain-punch', 'wild-charge', 'volt-switch'],
                'items': ['assault-vest', 'sitrus-berry', 'flame-orb'],
                'natures': ['adamant', 'brave'],
                'evs': {'hp': 252, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 4, 'speed': 0}
            },
            'tornadus-incarnate': {
                'role': 'support',
                'tier': 'S',
                'moves': ['tailwind', 'rain-dance', 'taunt', 'bleakwind-storm'],
                'items': ['focus-sash', 'mental-herb', 'covert-cloak'],
                'natures': ['timid', 'jolly'],
                'evs': {'hp': 4, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 0, 'speed': 252}
            },
            'ogerpon-hearthflame': {
                'role': 'physical-sweeper',
                'tier': 'S',
                'moves': ['ivy-cudgel', 'follow-me', 'spiky-shield', 'horn-leech'],
                'items': ['hearthflame-mask'],
                'natures': ['jolly', 'adamant'],
                'evs': {'hp': 4, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 252}
            },
            'raging-bolt': {
                'role': 'special-tank',
                'tier': 'A',
                'moves': ['thunderclap', 'dragon-pulse', 'calm-mind', 'weather-ball'],
                'items': ['assault-vest', 'life-orb', 'sitrus-berry'],
                'natures': ['modest', 'quiet'],
                'evs': {'hp': 252, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 4, 'speed': 0}
            },
            'terapagos': {
                'role': 'special-sweeper',
                'tier': 'A',
                'moves': ['tera-starstorm', 'earth-power', 'calm-mind', 'ancient-power'],
                'items': ['leftovers', 'sitrus-berry', 'life-orb'],
                'natures': ['modest', 'timid'],
                'evs': {'hp': 252, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 4, 'speed': 0}
            },
            'urshifu-rapid-strike': {
                'role': 'physical-sweeper',
                'tier': 'A',
                'moves': ['surging-strikes', 'close-combat', 'aqua-jet', 'protect'],
                'items': ['focus-sash', 'life-orb', 'mystic-water'],
                'natures': ['jolly', 'adamant'],
                'evs': {'hp': 0, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 4, 'speed': 252}
            },
            'chi-yu': {
                'role': 'special-sweeper',
                'tier': 'A',
                'moves': ['heat-wave', 'dark-pulse', 'snarl', 'protect'],
                'items': ['focus-sash', 'life-orb'],
                'natures': ['timid', 'modest'],
                'evs': {'hp': 0, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 4, 'speed': 252}
            },
            'whimsicott': {
                'role': 'support',
                'tier': 'A',
                'moves': ['tailwind', 'encore', 'taunt', 'moonblast'],
                'items': ['focus-sash', 'mental-herb', 'covert-cloak'],
                'natures': ['timid', 'bold'],
                'evs': {'hp': 252, 'attack': 0, 'defense': 252, 'sp_attack': 0, 'sp_defense': 4, 'speed': 0}
            },
            'grimmsnarl': {
                'role': 'support',
                'tier': 'A',
                'moves': ['reflect', 'light-screen', 'spirit-break', 'fake-out'],
                'items': ['light-clay', 'sitrus-berry'],
                'natures': ['careful', 'impish'],
                'evs': {'hp': 252, 'attack': 4, 'defense': 252, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
            },
            'amoonguss': {
                'role': 'support',
                'tier': 'A',
                'moves': ['spore', 'rage-powder', 'pollen-puff', 'protect'],
                'items': ['sitrus-berry', 'rocky-helmet', 'focus-sash'],
                'natures': ['sassy', 'relaxed'],
                'evs': {'hp': 252, 'attack': 0, 'defense': 252, 'sp_attack': 0, 'sp_defense': 4, 'speed': 0}
            },
            'incineroar': {
                'role': 'support',
                'tier': 'A',
                'moves': ['fake-out', 'flare-blitz', 'knock-off', 'parting-shot'],
                'items': ['sitrus-berry', 'assault-vest', 'safety-goggles'],
                'natures': ['adamant', 'impish'],
                'evs': {'hp': 252, 'attack': 4, 'defense': 252, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
            },
            'landorus-therian': {
                'role': 'physical-sweeper',
                'tier': 'A',
                'moves': ['earthquake', 'u-turn', 'superpower', 'rock-slide'],
                'items': ['choice-scarf', 'life-orb', 'assault-vest'],
                'natures': ['jolly', 'adamant'],
                'evs': {'hp': 4, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 252}
            },
            'dragonite': {
                'role': 'physical-sweeper',
                'tier': 'B',
                'moves': ['extreme-speed', 'dragon-claw', 'earthquake', 'protect'],
                'items': ['choice-band', 'life-orb', 'lum-berry'],
                'natures': ['adamant', 'jolly'],
                'evs': {'hp': 4, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 252}
            },
            'garchomp': {
                'role': 'physical-sweeper',
                'tier': 'B',
                'moves': ['dragon-claw', 'earthquake', 'rock-slide', 'protect'],
                'items': ['life-orb', 'choice-scarf', 'focus-sash'],
                'natures': ['jolly', 'adamant'],
                'evs': {'hp': 4, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 252}
            },
            'gholdengo': {
                'role': 'special-sweeper',
                'tier': 'B',
                'moves': ['make-it-rain', 'shadow-ball', 'thunderbolt', 'protect'],
                'items': ['life-orb', 'focus-sash', 'choice-specs'],
                'natures': ['timid', 'modest'],
                'evs': {'hp': 4, 'attack': 0, 'defense': 0, 'sp_attack': 252, 'sp_defense': 0, 'speed': 252}
            },
            'kingambit': {
                'role': 'physical-tank',
                'tier': 'B',
                'moves': ['kowtow-cleave', 'sucker-punch', 'iron-head', 'protect'],
                'items': ['life-orb', 'focus-sash', 'chople-berry'],
                'natures': ['adamant', 'brave'],
                'evs': {'hp': 252, 'attack': 252, 'defense': 4, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
            },
        }
    
    def get_pokemon(self, name: str) -> Optional[Pokemon]:
        """从数据库获取宝可梦信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, name_zh, type1, type2, hp, attack, defense, 
                   sp_attack, sp_defense, speed, bst, usage_rate
            FROM pokemon WHERE name = ?
        ''', (name,))
        row = cursor.fetchone()
        
        if row:
            types = [row['type1']]
            if row['type2']:
                types.append(row['type2'])
            
            # 使用中文名映射
            name_zh = row['name_zh'] or POKEMON_NAMES_ZH.get(name, name)
            
            return Pokemon(
                name=row['name'],
                name_zh=name_zh,
                types=types,
                stats={
                    'hp': row['hp'],
                    'attack': row['attack'],
                    'defense': row['defense'],
                    'sp_attack': row['sp_attack'],
                    'sp_defense': row['sp_defense'],
                    'speed': row['speed']
                },
                bst=row['bst'],
                usage_rate=row['usage_rate'] or 0.0
            )
        return None
    
    def get_moves(self, pokemon_name: str) -> List[str]:
        """获取宝可梦可学习的技能"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT move_name FROM pokemon_moves 
            WHERE pokemon_name = ? 
            ORDER BY usage_rate DESC
            LIMIT 10
        ''', (pokemon_name,))
        return [row[0] for row in cursor.fetchall()]
    
    def calculate_type_coverage(self, types: List[str]) -> Dict[str, float]:
        """计算类型覆盖度"""
        coverage = {}
        for attack_type in types:
            if attack_type in self.type_chart:
                for defend_type, multiplier in self.type_chart[attack_type].items():
                    if defend_type not in coverage:
                        coverage[defend_type] = multiplier
                    else:
                        coverage[defend_type] = max(coverage[defend_type], multiplier)
        return coverage
    
    def calculate_type_weakness(self, types: List[str]) -> Dict[str, float]:
        """计算类型弱点"""
        weakness = {}
        for defend_type in types:
            for attack_type, chart in self.type_chart.items():
                if defend_type in chart:
                    multiplier = chart[defend_type]
                    if attack_type not in weakness:
                        weakness[attack_type] = multiplier
                    else:
                        weakness[attack_type] *= multiplier
        return weakness
    
    def find_resistances(self, weakness: Dict[str, float]) -> List[str]:
        """找出抗性类型"""
        return [t for t, m in weakness.items() if m < 1.0]
    
    def find_weaknesses(self, weakness: Dict[str, float]) -> List[str]:
        """找出弱点类型"""
        return [t for t, m in weakness.items() if m > 1.0]
    
    def create_team_slot(self, pokemon_name: str) -> Optional[TeamSlot]:
        """创建队伍配置"""
        pokemon = self.get_pokemon(pokemon_name)
        if not pokemon:
            return None
        
        # 获取VGC配置
        vgc_set = self.vgc_sets.get(pokemon_name, {})
        
        # 选择技能
        moves = vgc_set.get('moves', self.get_moves(pokemon_name)[:4])
        if len(moves) < 4:
            # 补充默认技能
            default_moves = ['protect', 'substitute', 'toxic', 'hidden-power']
            moves = moves + default_moves[:4-len(moves)]
        
        # 选择道具
        items = vgc_set.get('items', ['life-orb', 'focus-sash', 'sitrus-berry'])
        item = items[0] if items else 'life-orb'
        
        # 选择性格
        natures = vgc_set.get('natures', ['adamant'])
        nature = natures[0] if natures else 'adamant'
        
        # EV配置
        evs = vgc_set.get('evs', {'hp': 4, 'attack': 252, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 252})
        
        return TeamSlot(
            pokemon=pokemon,
            moves=moves[:4],
            item=item,
            ability='',
            nature=nature,
            evs=evs
        )
    
    def recommend_team(self, strategy: str = "balanced") -> List[Dict]:
        """推荐6只宝可梦的队伍"""
        team = []
        
        # 根据策略选择核心宝可梦
        if strategy == "trick-room":
            core_pokemon = ['skeledirge', 'armarouge', 'torkoal', 'farigiraf', 'iron-hands', 'flutter-mane']
        elif strategy == "offensive":
            core_pokemon = ['flutter-mane', 'iron-hands', 'urshifu-rapid-strike', 'chi-yu', 'landorus-therian', 'dragonite']
        elif strategy == "defensive":
            core_pokemon = ['dondozo', 'garganacl', 'corviknight', 'toxapex', 'amoonguss', 'incineroar']
        else:
            # 平衡队
            core_pokemon = ['flutter-mane', 'iron-hands', 'tornadus-incarnate', 'landorus-therian', 'incineroar', 'urshifu-rapid-strike']
        
        # 创建队伍配置
        for poke_name in core_pokemon:
            slot = self.create_team_slot(poke_name)
            if slot:
                team.append(slot.to_dict())
        
        return team
    
    def analyze_team(self, team_names: List[str]) -> Dict:
        """分析已有队伍的优缺点"""
        team = []
        for name in team_names:
            pokemon = self.get_pokemon(name)
            if pokemon:
                team.append(pokemon)
        
        if not team:
            return {"error": "没有找到指定的宝可梦"}
        
        all_types = []
        for pokemon in team:
            all_types.extend(pokemon.types)
        
        coverage = self.calculate_type_coverage(all_types)
        weakness = self.calculate_type_weakness(all_types)
        
        # 计算队伍平均种族值
        avg_bst = sum(p.bst for p in team) / len(team)
        
        return {
            'team_size': len(team),
            'avg_bst': round(avg_bst, 1),
            'type_coverage': coverage,
            'weaknesses': self.find_weaknesses(weakness),
            'resistances': self.find_resistances(weakness),
            'missing_coverage': self._find_missing_coverage(all_types),
            'recommendations': self._get_recommendations(team)
        }
    
    def _find_missing_coverage(self, team_types: List[str]) -> List[str]:
        """找出队伍缺少的打击面"""
        all_types = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 
                     'fighting', 'poison', 'ground', 'flying', 'psychic', 
                     'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy']
        
        current_coverage = self.calculate_type_coverage(team_types)
        
        missing = []
        for t in all_types:
            if t not in current_coverage or current_coverage[t] < 2.0:
                missing.append(t)
        
        return missing
    
    def _get_recommendations(self, team: List[Pokemon]) -> List[str]:
        """基于当前队伍给出补强建议"""
        all_types = []
        for pokemon in team:
            all_types.extend(pokemon.types)
        
        missing = self._find_missing_coverage(all_types)
        
        suggestions = []
        for needed_type in missing[:3]:
            suggestions.append(f"建议补充{needed_type}属性的宝可梦")
        
        return suggestions


def main():
    """测试推荐功能"""
    recommender = PokemonRecommender()
    
    print("=" * 70)
    print("🎮 宝可梦VGC队伍推荐系统")
    print("=" * 70)
    
    # 测试平衡队推荐
    print("\n📋 平衡队推荐:")
    print("-" * 70)
    team = recommender.recommend_team("balanced")
    for i, slot in enumerate(team, 1):
        types = "/".join(slot['types_zh'])
        moves = "/".join(slot['moves_zh'][:4])
        print(f"{i}. {slot['name_zh']} ({slot['name']})")
        print(f"   属性: {types} | BST: {slot['bst']}")
        print(f"   道具: {slot['item_zh']} | 性格: {slot['nature_zh']}")
        print(f"   技能: {moves}")
        print()
    
    # 测试戏法空间队
    print("\n📋 戏法空间队推荐:")
    print("-" * 70)
    team = recommender.recommend_team("trick-room")
    for i, slot in enumerate(team, 1):
        types = "/".join(slot['types_zh'])
        print(f"{i}. {slot['name_zh']} ({slot['name']}) - {types} - BST:{slot['bst']}")


if __name__ == "__main__":
    main()
