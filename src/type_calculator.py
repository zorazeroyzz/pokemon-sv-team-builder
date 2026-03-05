# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 属性计算器
"""
import json
from typing import List, Dict, Tuple, Set
from pathlib import Path


class TypeCalculator:
    """宝可梦属性计算器"""
    
    # 属性列表
    TYPES = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
        'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
    ]
    
    # 属性相克矩阵 (攻击方 -> 防御方 = 伤害倍数)
    # 行: 攻击方属性, 列: 防御方属性
    TYPE_CHART = {
        'Normal':   {'Rock': 0.5, 'Ghost': 0, 'Steel': 0.5},
        'Fire':     {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 2, 'Bug': 2, 
                     'Rock': 0.5, 'Dragon': 0.5, 'Steel': 2},
        'Water':    {'Fire': 2, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2, 
                     'Rock': 2, 'Dragon': 0.5},
        'Electric': {'Water': 2, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0,
                     'Flying': 2, 'Dragon': 0.5},
        'Grass':    {'Fire': 0.5, 'Water': 2, 'Grass': 0.5, 'Poison': 0.5,
                     'Ground': 2, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2,
                     'Dragon': 0.5, 'Steel': 0.5},
        'Ice':      {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 0.5,
                     'Ground': 2, 'Flying': 2, 'Dragon': 2, 'Steel': 0.5},
        'Fighting': {'Normal': 2, 'Ice': 2, 'Poison': 0.5, 'Flying': 0.5,
                     'Psychic': 0.5, 'Bug': 0.5, 'Rock': 2, 'Ghost': 0,
                     'Dark': 2, 'Steel': 2, 'Fairy': 0.5},
        'Poison':   {'Grass': 2, 'Poison': 0.5, 'Ground': 0.5, 'Rock': 0.5,
                     'Ghost': 0.5, 'Steel': 0, 'Fairy': 2},
        'Ground':   {'Fire': 2, 'Electric': 2, 'Grass': 0.5, 'Poison': 2,
                     'Flying': 0, 'Bug': 0.5, 'Rock': 2, 'Steel': 2},
        'Flying':   {'Electric': 0.5, 'Grass': 2, 'Fighting': 2, 'Bug': 2,
                     'Rock': 0.5, 'Steel': 0.5},
        'Psychic':  {'Fighting': 2, 'Poison': 2, 'Psychic': 0.5, 'Dark': 0,
                     'Steel': 0.5},
        'Bug':      {'Fire': 0.5, 'Grass': 2, 'Fighting': 0.5, 'Poison': 0.5,
                     'Flying': 0.5, 'Psychic': 2, 'Ghost': 0.5, 'Dark': 2,
                     'Steel': 0.5, 'Fairy': 0.5},
        'Rock':     {'Fire': 2, 'Ice': 2, 'Fighting': 0.5, 'Ground': 0.5,
                     'Flying': 2, 'Bug': 2, 'Steel': 0.5},
        'Ghost':    {'Normal': 0, 'Psychic': 2, 'Ghost': 2, 'Dark': 0.5},
        'Dragon':   {'Dragon': 2, 'Steel': 0.5, 'Fairy': 0},
        'Dark':     {'Fighting': 0.5, 'Psychic': 2, 'Ghost': 2, 'Dark': 0.5,
                     'Fairy': 0.5},
        'Steel':    {'Fire': 0.5, 'Water': 0.5, 'Electric': 0.5, 'Ice': 2,
                     'Rock': 2, 'Steel': 0.5, 'Fairy': 2},
        'Fairy':    {'Fire': 0.5, 'Fighting': 2, 'Poison': 0.5, 'Dragon': 2,
                     'Dark': 2, 'Steel': 0.5}
    }
    
    def __init__(self):
        self.type_chart = self.TYPE_CHART
    
    def get_effectiveness(self, attack_type: str, defense_type: str) -> float:
        """
        获取攻击属性对防御属性的效果
        返回: 0 (无效), 0.5 (效果不好), 1 (正常), 2 (效果拔群)
        """
        if attack_type not in self.type_chart:
            return 1.0
        
        return self.type_chart[attack_type].get(defense_type, 1.0)
    
    def get_dual_type_effectiveness(self, attack_type: str, 
                                     defense_type1: str, 
                                     defense_type2: str = None) -> float:
        """计算攻击属性对双属性防御方的效果"""
        effectiveness1 = self.get_effectiveness(attack_type, defense_type1)
        
        if defense_type2 and defense_type2 != defense_type1:
            effectiveness2 = self.get_effectiveness(attack_type, defense_type2)
            return effectiveness1 * effectiveness2
        
        return effectiveness1
    
    def get_defensive_coverage(self, type1: str, type2: str = None) -> Dict[str, float]:
        """
        获取某属性的防御面（各属性对其造成的伤害倍数）
        返回: {攻击属性: 伤害倍数}
        """
        coverage = {}
        for attack_type in self.TYPES:
            effectiveness = self.get_dual_type_effectiveness(attack_type, type1, type2)
            coverage[attack_type] = effectiveness
        return coverage
    
    def get_offensive_coverage(self, types: List[str]) -> Dict[str, float]:
        """
        获取属性组合的攻击面（对各属性造成的伤害倍数）
        取最高效果
        """
        coverage = {}
        for defense_type in self.TYPES:
            max_effectiveness = 0
            for attack_type in types:
                effectiveness = self.get_effectiveness(attack_type, defense_type)
                max_effectiveness = max(max_effectiveness, effectiveness)
            coverage[defense_type] = max_effectiveness
        return coverage
    
    def analyze_team_defensive_coverage(self, team_types: List[Tuple[str, str]]) -> Dict:
        """
        分析队伍的防御面
        team_types: [(type1, type2), ...] 6只宝可梦的属性组合
        """
        # 统计各属性对队伍造成的伤害
        type_damage = {t: [] for t in self.TYPES}
        
        for type1, type2 in team_types:
            defense_coverage = self.get_defensive_coverage(type1, type2)
            for attack_type, damage in defense_coverage.items():
                type_damage[attack_type].append(damage)
        
        # 分析结果
        analysis = {
            'weaknesses': [],      # 队伍整体弱点（多个成员被克制）
            'resistances': [],     # 队伍整体抗性
            'immunities': [],      # 免疫的属性
            'type_damage': type_damage
        }
        
        for attack_type, damages in type_damage.items():
            avg_damage = sum(damages) / len(damages) if damages else 0
            max_damage = max(damages) if damages else 0
            
            if max_damage == 0:
                analysis['immunities'].append(attack_type)
            elif avg_damage >= 1.5:
                analysis['weaknesses'].append({
                    'type': attack_type,
                    'avg_damage': avg_damage,
                    'max_damage': max_damage
                })
            elif avg_damage <= 0.5:
                analysis['resistances'].append({
                    'type': attack_type,
                    'avg_damage': avg_damage
                })
        
        return analysis
    
    def analyze_team_offensive_coverage(self, team_types: List[Tuple[str, str]]) -> Dict:
        """分析队伍的攻击面覆盖"""
        # 收集队伍所有属性
        all_types = set()
        for type1, type2 in team_types:
            all_types.add(type1)
            if type2:
                all_types.add(type2)
        
        # 计算攻击覆盖
        coverage = self.get_offensive_coverage(list(all_types))
        
        analysis = {
            'super_effective': [],    # 效果拔群的属性
            'neutral': [],            # 正常伤害的属性
            'not_very_effective': [], # 效果不好的属性
            'no_effect': [],          # 无效的属性
            'coverage_score': 0       # 覆盖评分
        }
        
        for defense_type, effectiveness in coverage.items():
            if effectiveness >= 2:
                analysis['super_effective'].append(defense_type)
            elif effectiveness == 0:
                analysis['no_effect'].append(defense_type)
            elif effectiveness < 1:
                analysis['not_very_effective'].append(defense_type)
            else:
                analysis['neutral'].append(defense_type)
        
        # 计算覆盖评分 (效果拔群属性数 / 总属性数)
        analysis['coverage_score'] = len(analysis['super_effective']) / len(self.TYPES)
        
        return analysis
    
    def calculate_synergy_score(self, pokemon1_types: Tuple[str, str], 
                                pokemon2_types: Tuple[str, str]) -> float:
        """
        计算两只宝可梦的联防评分
        考虑：属性互补、弱点覆盖
        """
        score = 0.0
        
        # 获取各自的防御面
        coverage1 = self.get_defensive_coverage(pokemon1_types[0], pokemon1_types[1])
        coverage2 = self.get_defensive_coverage(pokemon2_types[0], pokemon2_types[1])
        
        # 检查互补性：如果一方弱点是另一方抗性，加分
        for attack_type in self.TYPES:
            damage1 = coverage1[attack_type]
            damage2 = coverage2[attack_type]
            
            # 弱点互补
            if damage1 > 1 and damage2 < 1:
                score += (damage1 - damage2) * 0.5
            elif damage2 > 1 and damage1 < 1:
                score += (damage2 - damage1) * 0.5
            
            # 共同抗性
            if damage1 < 1 and damage2 < 1:
                score += 0.1
        
        return score
    
    def get_type_weaknesses(self, type1: str, type2: str = None) -> List[str]:
        """获取属性的弱点列表"""
        weaknesses = []
        coverage = self.get_defensive_coverage(type1, type2)
        for attack_type, damage in coverage.items():
            if damage > 1:
                weaknesses.append(attack_type)
        return weaknesses
    
    def get_type_resistances(self, type1: str, type2: str = None) -> List[str]:
        """获取属性的抗性列表"""
        resistances = []
        coverage = self.get_defensive_coverage(type1, type2)
        for attack_type, damage in coverage.items():
            if damage < 1 and damage > 0:
                resistances.append(attack_type)
        return resistances
    
    def get_type_immunities(self, type1: str, type2: str = None) -> List[str]:
        """获取属性的免疫列表"""
        immunities = []
        coverage = self.get_defensive_coverage(type1, type2)
        for attack_type, damage in coverage.items():
            if damage == 0:
                immunities.append(attack_type)
        return immunities
