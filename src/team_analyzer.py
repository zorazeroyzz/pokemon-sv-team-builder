# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 队伍分析器
"""
from typing import List, Dict, Tuple, Optional
from collections import Counter
import random

from .database import PokemonDatabase
from .type_calculator import TypeCalculator


class TeamAnalyzer:
    """队伍分析器"""
    
    def __init__(self, db: PokemonDatabase):
        self.db = db
        self.type_calc = TypeCalculator()
    
    def analyze_team(self, team: List[str], format_name: str = 'gen9vgc2026regf') -> Dict:
        """
        分析一个队伍的完整信息
        team: 6只宝可梦的名称列表
        """
        if len(team) != 6:
            raise ValueError("队伍必须包含6只宝可梦")
        
        # 获取宝可梦详细信息
        pokemon_details = []
        for name in team:
            p = self.db.get_pokemon_by_name(name)
            if p:
                pokemon_details.append(p)
        
        if len(pokemon_details) != 6:
            raise ValueError(f"部分宝可梦数据缺失: {team}")
        
        # 提取属性组合
        team_types = [(p['type1'], p['type2']) for p in pokemon_details]
        
        # 防御面分析
        defensive_analysis = self.type_calc.analyze_team_defensive_coverage(team_types)
        
        # 攻击面分析
        offensive_analysis = self.type_calc.analyze_team_offensive_coverage(team_types)
        
        # 计算队伍协同性
        synergy_score = self._calculate_team_synergy(team_types)
        
        # 计算热门度（使用率总和）
        popularity_score = sum(p.get('usage_rate', 0) for p in pokemon_details) / 6
        
        # 种族值分析
        bst_stats = {
            'avg_bst': sum(p.get('bst', 0) for p in pokemon_details) / 6,
            'avg_hp': sum(p.get('hp', 0) for p in pokemon_details) / 6,
            'avg_attack': sum(p.get('attack', 0) for p in pokemon_details) / 6,
            'avg_defense': sum(p.get('defense', 0) for p in pokemon_details) / 6,
            'avg_sp_attack': sum(p.get('sp_attack', 0) for p in pokemon_details) / 6,
            'avg_sp_defense': sum(p.get('sp_defense', 0) for p in pokemon_details) / 6,
            'avg_speed': sum(p.get('speed', 0) for p in pokemon_details) / 6,
        }
        
        # 属性多样性
        type_counter = Counter()
        for p in pokemon_details:
            type_counter[p['type1']] += 1
            if p['type2']:
                type_counter[p['type2']] += 1
        
        return {
            'team': team,
            'pokemon_details': pokemon_details,
            'defensive_analysis': defensive_analysis,
            'offensive_analysis': offensive_analysis,
            'synergy_score': synergy_score,
            'popularity_score': popularity_score,
            'bst_stats': bst_stats,
            'type_distribution': dict(type_counter),
            'overall_score': self._calculate_overall_score(
                synergy_score, offensive_analysis['coverage_score'], 
                defensive_analysis, popularity_score
            )
        }
    
    def _calculate_team_synergy(self, team_types: List[Tuple[str, str]]) -> float:
        """计算队伍整体协同性"""
        total_synergy = 0.0
        count = 0
        
        for i in range(len(team_types)):
            for j in range(i + 1, len(team_types)):
                synergy = self.type_calc.calculate_synergy_score(
                    team_types[i], team_types[j]
                )
                total_synergy += synergy
                count += 1
        
        return total_synergy / count if count > 0 else 0
    
    def _calculate_overall_score(self, synergy: float, coverage: float, 
                                  defense: Dict, popularity: float) -> float:
        """计算队伍综合评分"""
        # 弱点惩罚
        weakness_penalty = len(defense.get('weaknesses', [])) * 0.1
        
        # 综合评分公式
        score = (
            synergy * 0.3 +           # 协同性 30%
            coverage * 0.3 +          # 攻击覆盖 30%
            (1 - weakness_penalty) * 0.2 +  # 防御稳健 20%
            min(popularity / 30, 1) * 0.2   # 热门度 20% (封顶30%)
        )
        
        return max(0, min(10, score * 10))  # 0-10分
    
    def find_core_combinations(self, format_name: str = 'gen9vgc2026regf', 
                               top_n: int = 20) -> List[Tuple[List[str], float]]:
        """
        寻找热门的核心组合（2-3只宝可梦的强力组合）
        """
        # 获取热门宝可梦
        top_pokemon = self.db.get_all_pokemon(format_name, limit=top_n)
        
        cores = []
        
        # 检查2人组合
        for i in range(len(top_pokemon)):
            for j in range(i + 1, len(top_pokemon)):
                p1, p2 = top_pokemon[i], top_pokemon[j]
                
                # 计算协同性
                synergy = self.type_calc.calculate_synergy_score(
                    (p1['type1'], p1['type2']),
                    (p2['type1'], p2['type2'])
                )
                
                # 检查队友关联
                teammates1 = self.db.get_pokemon_teammates(p1['name'], format_name, limit=10)
                teammates2 = self.db.get_pokemon_teammates(p2['name'], format_name, limit=10)
                
                teammate_names1 = {t['teammate_name'] for t in teammates1}
                teammate_names2 = {t['teammate_name'] for t in teammates2}
                
                # 如果互相是队友，加分
                synergy_bonus = 0
                if p2['name'] in teammate_names1:
                    synergy_bonus += 0.5
                if p1['name'] in teammate_names2:
                    synergy_bonus += 0.5
                
                total_score = synergy + synergy_bonus
                
                if total_score > 0.5:
                    cores.append(([p1['name'], p2['name']], total_score))
        
        # 按分数排序
        cores.sort(key=lambda x: x[1], reverse=True)
        return cores[:20]
    
    def generate_team_candidates(self, format_name: str = 'gen9vgc2026regf',
                                  style: str = 'balanced',
                                  core: List[str] = None) -> List[List[str]]:
        """
        生成候选队伍
        style: 'balanced', 'offensive', 'defensive'
        core: 指定核心宝可梦（2-3只）
        """
        # 获取候选池
        if style == 'offensive':
            # 进攻型：优先高攻击、高速
            candidates = self.db.get_all_pokemon(format_name, limit=30)
            candidates.sort(key=lambda p: p.get('attack', 0) + p.get('sp_attack', 0) + p.get('speed', 0), reverse=True)
        elif style == 'defensive':
            # 防守型：优先高耐久
            candidates = self.db.get_all_pokemon(format_name, limit=30)
            candidates.sort(key=lambda p: p.get('hp', 0) + p.get('defense', 0) + p.get('sp_defense', 0), reverse=True)
        else:
            # 平衡型：按使用率
            candidates = self.db.get_all_pokemon(format_name, limit=40)
        
        candidate_names = [p['name'] for p in candidates]
        
        teams = []
        
        if core and len(core) >= 2:
            # 以核心为基础，补充其他成员
            remaining_slots = 6 - len(core)
            
            # 获取核心的推荐队友
            recommended_teammates = set()
            for core_member in core:
                teammates = self.db.get_pokemon_teammates(core_member, format_name, limit=10)
                for t in teammates:
                    if t['teammate_name'] not in core:
                        recommended_teammates.add(t['teammate_name'])
            
            # 从推荐队友中选择
            available_teammates = list(recommended_teammates.intersection(set(candidate_names)))
            
            # 生成组合
            from itertools import combinations
            if len(available_teammates) >= remaining_slots:
                for combo in combinations(available_teammates[:15], remaining_slots):
                    team = list(core) + list(combo)
                    teams.append(team)
        else:
            # 无核心，从热门宝可梦中生成
            from itertools import combinations
            for combo in combinations(candidate_names[:15], 6):
                teams.append(list(combo))
        
        return teams[:50]  # 限制候选数量
    
    def score_team_for_style(self, team_analysis: Dict, style: str) -> float:
        """根据风格给队伍打分"""
        score = team_analysis['overall_score']
        
        if style == 'offensive':
            # 进攻型：重视攻击覆盖、高攻击种族值
            coverage = team_analysis['offensive_analysis']['coverage_score']
            atk_stats = team_analysis['bst_stats']['avg_attack'] + team_analysis['bst_stats']['avg_sp_attack']
            speed = team_analysis['bst_stats']['avg_speed']
            
            score = coverage * 4 + atk_stats / 50 + speed / 30
            
        elif style == 'defensive':
            # 防守型：重视抗性、高耐久
            resistances = len(team_analysis['defensive_analysis'].get('resistances', []))
            weaknesses = len(team_analysis['defensive_analysis'].get('weaknesses', []))
            bulk = (team_analysis['bst_stats']['avg_hp'] + 
                   team_analysis['bst_stats']['avg_defense'] + 
                   team_analysis['bst_stats']['avg_sp_defense'])
            
            score = resistances * 0.5 - weaknesses * 0.3 + bulk / 50
            
        else:  # balanced
            # 平衡型：使用默认评分
            pass
        
        return score
