# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 自动更新模块
"""
import os
import sys
import json
import sqlite3
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))
from src.database import PokemonDatabase
from src.data_collector import PikalyticsCollector, POKEMON_NAME_ZH
from src.type_calculator import TypeCalculator
from src.team_analyzer import TeamAnalyzer


@dataclass
class RegulationInfo:
    current_reg: str = "Regulation F"
    start_date: str = "2024-09-01"
    end_date: str = "2026-03-31"
    next_reg: str = ""
    next_start_date: str = ""
    is_active: bool = True
    last_checked: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TavilyRuleChecker:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('TAVILY_API_KEY', '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')
        self.base_url = "https://api.tavily.com/search"
        self.regulation_file = Path(__file__).parent / "data" / "regulation_info.json"
        
    def load_regulation_info(self) -> RegulationInfo:
        if self.regulation_file.exists():
            try:
                with open(self.regulation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return RegulationInfo(**data)
            except Exception as e:
                logger.error(f"加载规则信息失败: {e}")
        return RegulationInfo()
    
    def save_regulation_info(self, info: RegulationInfo):
        self.regulation_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.regulation_file, 'w', encoding='utf-8') as f:
            json.dump(info.to_dict(), f, ensure_ascii=False, indent=2)
    
    def check_regulation_update(self) -> Tuple[bool, str, RegulationInfo]:
        current_info = self.load_regulation_info()
        
        try:
            query = "Pokemon Scarlet Violet VGC 2026 Regulation F G H new rules"
            
            response = requests.post(
                self.base_url,
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "max_results": 5
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            answer = data.get('answer', '')
            results = data.get('results', [])
            
            logger.info(f"Tavily搜索完成，获取到 {len(results)} 条结果")
            
            new_regulation = self._detect_new_regulation(answer, results)
            
            current_info.last_checked = datetime.now().isoformat()
            
            if new_regulation and new_regulation != current_info.current_reg:
                old_reg = current_info.current_reg
                current_info.current_reg = new_regulation
                current_info.start_date = datetime.now().strftime("%Y-%m-%d")
                end_date = datetime.now() + timedelta(days=180)
                current_info.end_date = end_date.strftime("%Y-%m-%d")
                
                self.save_regulation_info(current_info)
                
                msg = f"发现新规则！{old_reg} -> {new_regulation}"
                logger.info(msg)
                return True, msg, current_info
            
            days_remaining = self._calculate_days_remaining(current_info.end_date)
            
            if days_remaining <= 0:
                current_info.is_active = False
                msg = f"当前规则 {current_info.current_reg} 已结束，请检查新规则"
            elif days_remaining <= 30:
                msg = f"当前规则 {current_info.current_reg} 将在 {days_remaining} 天后结束 ({current_info.end_date})"
            else:
                msg = f"当前规则 {current_info.current_reg} 正常运行，剩余 {days_remaining} 天"
            
            self.save_regulation_info(current_info)
            logger.info(msg)
            return False, msg, current_info
            
        except Exception as e:
            logger.error(f"检查规则更新失败: {e}")
            return False, f"检查失败: {e}", current_info
    
    def _detect_new_regulation(self, answer: str, results: List[Dict]) -> Optional[str]:
        import re
        
        all_text = answer + " " + " ".join([r.get('content', '') for r in results])
        all_text += " " + " ".join([r.get('title', '') for r in results])
        
        patterns = [
            r'Regulation\s+([A-Z])',
            r'Reg\s+([A-Z])',
            r'规则([A-Z])',
        ]
        
        found_regs = []
        for pattern in patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            found_regs.extend([f"Regulation {m.upper()}" for m in matches])
        
        found_regs = list(set(found_regs))
        
        reg_order = {'Regulation A': 1, 'Regulation B': 2, 'Regulation C': 3,
                     'Regulation D': 4, 'Regulation E': 5, 'Regulation F': 6,
                     'Regulation G': 7, 'Regulation H': 8, 'Regulation I': 9}
        
        current_order = reg_order.get('Regulation F', 6)
        
        for reg in found_regs:
            if reg in reg_order and reg_order[reg] > current_order:
                return reg
        
        return None
    
    def _calculate_days_remaining(self, end_date_str: str) -> int:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            today = datetime.now()
            return (end_date - today).days
        except:
            return 999


class PikalyticsDataUpdater:
    def __init__(self):
        self.db = PokemonDatabase()
        self.collector = PikalyticsCollector()
        self.history_file = Path(__file__).parent / "data" / "usage_history.db"
        
    def init_history_db(self):
        conn = sqlite3.connect(self.history_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_name TEXT NOT NULL,
                usage_rate REAL,
                format TEXT,
                date TEXT DEFAULT CURRENT_DATE,
                UNIQUE(pokemon_name, format, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT CURRENT_DATE,
                format TEXT,
                top_pokemon TEXT,
                core_combinations TEXT,
                meta_analysis TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("历史数据库初始化完成")
    
    def update_all_data(self, limit: int = 50) -> Dict:
        import time
        stats = {
            'updated': 0,
            'failed': 0,
            'new_entries': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"开始更新数据，限制: {limit} 只宝可梦")
        
        pokemon_list = self.collector.TOP_POKEMON[:limit]
        
        for i, pokemon_name in enumerate(pokemon_list, 1):
            logger.info(f"[{i}/{len(pokemon_list)}] 更新 {pokemon_name}...")
            
            try:
                data = self.collector.fetch_pokemon_data(pokemon_name)
                if data:
                    self._update_pokemon_data(data)
                    self._record_usage_history(data)
                    stats['updated'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                logger.error(f"更新 {pokemon_name} 失败: {e}")
                stats['failed'] += 1
            
            time.sleep(0.5)
        
        logger.info(f"数据更新完成: {stats['updated']} 成功, {stats['failed']} 失败")
        return stats
    
    def _update_pokemon_data(self, data: Dict):
        self.db.insert_pokemon({
            'name': data['name'],
            'name_zh': POKEMON_NAME_ZH.get(data['name'], ''),
            'type1': data.get('type1', 'Normal'),
            'type2': data.get('type2'),
            'hp': data.get('hp', 0),
            'attack': data.get('attack', 0),
            'defense': data.get('defense', 0),
            'sp_attack': data.get('sp_attack', 0),
            'sp_defense': data.get('sp_defense', 0),
            'speed': data.get('speed', 0),
            'bst': data.get('bst', 0),
            'usage_rate': data.get('usage_rate', 0),
            'format': self.collector.FORMAT
        })
        
        for move in data.get('moves', []):
            self.db.insert_move({'name': move['name']})
            self.db.insert_pokemon_move(
                data['name'], move['name'], 
                move['usage_rate'], self.collector.FORMAT
            )
        
        for item in data.get('items', []):
            self.db.insert_item({'name': item['name']})
            self.db.insert_pokemon_item(
                data['name'], item['name'],
                item['usage_rate'], self.collector.FORMAT
            )
        
        for teammate in data.get('teammates', []):
            self.db.insert_pokemon_teammate(
                data['name'], teammate['name'],
                teammate['synergy_rate'], self.collector.FORMAT
            )
    
    def _record_usage_history(self, data: Dict):
        conn = sqlite3.connect(self.history_file)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT OR REPLACE INTO usage_history 
            (pokemon_name, usage_rate, format, date)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data.get('usage_rate', 0), self.collector.FORMAT, today))
        
        conn.commit()
        conn.close()


class MetaAnalyzer:
    def __init__(self):
        self.db = PokemonDatabase()
        self.analyzer = TeamAnalyzer(self.db)
        self.type_calc = TypeCalculator()
        
    def analyze_current_meta(self) -> Dict:
        logger.info("开始分析当前环境...")
        
        top_pokemon = self.db.get_all_pokemon('gen9vgc2026regf', limit=30)
        core_combos = self.analyzer.find_core_combinations('gen9vgc2026regf', top_n=20)
        type_distribution = self._analyze_type_distribution(top_pokemon)
        popular_items = self._analyze_popular_items(top_pokemon[:20])
        trends = self._analyze_trends(top_pokemon)
        
        analysis = {
            'date': datetime.now().isoformat(),
            'format': 'gen9vgc2026regf',
            'top_pokemon': [
                {
                    'name': p['name'],
                    'name_zh': POKEMON_NAME_ZH.get(p['name'], ''),
                    'usage_rate': p.get('usage_rate', 0),
                    'types': [p['type1'], p['type2']] if p['type2'] else [p['type1']]
                }
                for p in top_pokemon[:20]
            ],
            'core_combinations': [
                {
                    'members': combo[0],
                    'score': combo[1],
                    'members_zh': [POKEMON_NAME_ZH.get(m, '') for m in combo[0]]
                }
                for combo in core_combos[:10]
            ],
            'type_distribution': type_distribution,
            'popular_items': popular_items,
            'trends': trends,
            'summary': self._generate_meta_summary(top_pokemon, core_combos, type_distribution)
        }
        
        self._save_meta_analysis(analysis)
        
        logger.info("环境分析完成")
        return analysis
    
    def _analyze_type_distribution(self, pokemon_list: List[Dict]) -> Dict:
        from collections import Counter
        
        type_counter = Counter()
        for p in pokemon_list:
            type_counter[p['type1']] += 1
            if p['type2']:
                type_counter[p['type2']] += 1
        
        return dict(type_counter.most_common())
    
    def _analyze_popular_items(self, pokemon_list: List[Dict]) -> List[Dict]:
        item_counter = {}
        
        for p in pokemon_list:
            items = self.db.get_pokemon_items(p['name'], 'gen9vgc2026regf', limit=3)
            for item in items:
                name = item['item_name']
                if name not in item_counter:
                    item_counter[name] = {'count': 0, 'total_usage': 0}
                item_counter[name]['count'] += 1
                item_counter[name]['total_usage'] += item['usage_rate']
        
        sorted_items = sorted(
            item_counter.items(),
            key=lambda x: x[1]['total_usage'],
            reverse=True
        )
        
        return [
            {'name': name, 'popularity': data['count'], 'total_usage': data['total_usage']}
            for name, data in sorted_items[:15]
        ]
    
    def _analyze_trends(self, current_pokemon: List[Dict]) -> Dict:
        history_file = Path(__file__).parent / "data" / "usage_history.db"
        
        if not history_file.exists():
            return {'message': '暂无历史数据'}
        
        try:
            conn = sqlite3.connect(history_file)
            cursor = conn.cursor()
            
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT pokemon_name, usage_rate FROM usage_history
                WHERE date <= ? AND format = ?
                ORDER BY date DESC
            ''', (week_ago, 'gen9vgc2026regf'))
            
            old_data = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            
            rising = []
            falling = []
            
            for p in current_pokemon[:30]:
                name = p['name']
                current_rate = p.get('usage_rate', 0)
                old_rate = old_data.get(name, current_rate)
                
                change = current_rate - old_rate
                
                if change > 2:
                    rising.append({'name': name, 'change': change})
                elif change < -2:
                    falling.append({'name': name, 'change': change})
            
            return {
                'rising': sorted(rising, key=lambda x: x['change'], reverse=True)[:5],
                'falling': sorted(falling, key=lambda x: x['change'])[:5]
            }
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {'error': str(e)}
    
    def _generate_meta_summary(self, top_pokemon: List[Dict], 
                               core_combos: List, type_dist: Dict) -> str:
        summary_parts = []
        
        top3 = [POKEMON_NAME_ZH.get(p['name'], p['name']) for p in top_pokemon[:3]]
        summary_parts.append(f"当前环境头部: {', '.join(top3)}")
        
        top_types = list(type_dist.keys())[:3]
        summary_parts.append(f"热门属性: {', '.join(top_types)}")
        
        if core_combos:
            combo_names = [f"{POKEMON_NAME_ZH.get(c[0][0], c[0][0])}+{POKEMON_NAME_ZH.get(c[0][1], c[0][1])}" 
                          for c in core_combos[:3]]
            summary_parts.append(f"热门组合: {', '.join(combo_names)}")
        
        return " | ".join(summary_parts)
    
    def _save_meta_analysis(self, analysis: Dict):
        history_file = Path(__file__).parent / "data" / "usage_history.db"
        
        try:
            conn = sqlite3.connect(history_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meta_snapshot 
                (date, format, top_pokemon, core_combinations, meta_analysis)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d"),
                analysis['format'],
                json.dumps(analysis['top_pokemon']),
                json.dumps(analysis['core_combinations']),
                analysis['summary']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存环境分析失败: {e}")


class CounterTeamRecommender:
    def __init__(self):
        self.db = PokemonDatabase()
        self.analyzer = TeamAnalyzer(self.db)
        self.type_calc = TypeCalculator()
        
    def generate_counter_teams(self, meta_analysis: Dict) -> Dict:
        logger.info("开始生成克制队伍推荐...")
        
        top_threats = [p['name'] for p in meta_analysis['top_pokemon'][:10]]
        threat_weaknesses = self._analyze_threat_weaknesses(top_threats)
        counter_candidates = self._find_counter_candidates(threat_weaknesses)
        counter_teams = self._build_counter_teams(
            counter_candidates, 
            top_threats,
            meta_analysis['type_distribution']
        )
        ai_analysis = self._generate_ai_counter_analysis(
            meta_analysis, 
            counter_teams,
            threat_weaknesses
        )
        
        result = {
            'date': datetime.now().isoformat(),
            'target_meta': meta_analysis['summary'],
            'threats_analyzed': [
                {
                    'name': name,
                    'name_zh': POKEMON_NAME_ZH.get(name, ''),
                    'weaknesses': threat_weaknesses.get(name, [])
                }
                for name in top_threats[:5]
            ],
            'recommended_counter_teams': counter_teams,
            'ai_analysis': ai_analysis
        }
        
        self._save_counter_recommendation(result)
        
        logger.info("克制队伍推荐生成完成")
        return result
    
    def _analyze_threat_weaknesses(self, threats: List[str]) -> Dict[str, List[str]]:
        weaknesses = {}
        
        for name in threats:
            pokemon = self.db.get_pokemon_by_name(name)
            if pokemon:
                types = (pokemon['type1'], pokemon['type2'])
                type_weaknesses = self.type_calc.get_type_weaknesses(types)
                weaknesses[name] = type_weaknesses
        
        return weaknesses
    
    def _find_counter_candidates(self, threat_weaknesses: Dict) -> Dict[str, List[str]]:
        effective_types = {}
        
        for threat, weaknesses in threat_weaknesses.items():
            for w_type in weaknesses:
                if w_type not in effective_types:
                    effective_types[w_type] = []
                effective_types[w_type].append(threat)
        
        all_pokemon = self.db.get_all_pokemon('gen9vgc2026regf', limit=50)
        
        counters_by_type = {}
        
        for p in all_pokemon:
            p_types = [p['type1']]
            if p['type2']:
                p_types.append(p['type2'])
            
            for p_type in p_types:
                if p_type in effective_types:
                    if p_type not in counters_by_type:
                        counters_by_type[p_type] = []
                    counters_by_type[p_type].append(p['name'])
        
        return counters_by_type
    
    def _build_counter_teams(self, counter_candidates: Dict, 
                            threats: List[str],
                            type_distribution: Dict) -> List[Dict]:
        teams = []
        
        threat_data = []
        for name in threats[:5]:
            p = self.db.get_pokemon_by_name(name)
            if p:
                threat_data.append(p)
        
        if type_distribution:
            top_type = list(type_distribution.keys())[0]
            counter_type = self._get_counter_type(top_type)
            
            if counter_type and counter_type in counter_candidates:
                candidates = counter_candidates[counter_type][:6]
                if len(candidates) >= 4:
                    teams.append({
                        'name': f'反{top_type}特化队',
                        'strategy': f'针对当前热门{top_type}属性',
                        'core_types': [counter_type],
                        'members': candidates[:6],
                        'members_zh': [POKEMON_NAME_ZH.get(m, '') for m in candidates[:6]],
                        'target': f'克制{top_type}属性宝可梦'
                    })
        
        all_counters = []
        for type_name, pokemon_list in counter_candidates.items():
            all_counters.extend(pokemon_list[:3])
        
        unique_counters = list(dict.fromkeys(all_counters))[:6]
        if len(unique_counters) >= 4:
            teams.append({
                'name': '综合反制队',
                'strategy': '针对多种热门威胁的平衡队伍',
                'core_types': list(counter_candidates.keys())[:3],
                'members': unique_counters,
                'members_zh': [POKEMON_NAME_ZH.get(m, '') for m in unique_counters],
                'target': '全面克制热门宝可梦'
            })
        
        fast_counters = self._get_fast_counters(threats)
        if len(fast_counters) >= 4:
            teams.append({
                'name': '高速压制队',
                'strategy': '利用速度优势压制热门威胁',
                'core_types': [],
                'members': fast_counters[:6],
                'members_zh': [POKEMON_NAME_ZH.get(m, '') for m in fast_counters[:6]],
                'target': '速度线压制'
            })
        
        return teams
    
    def _get_counter_type(self, target_type: str) -> Optional[str]:
        counter_map = {
            'Fire': 'Water', 'Water': 'Electric', 'Electric': 'Ground',
            'Grass': 'Fire', 'Ice': 'Fire', 'Fighting': 'Psychic',
            'Poison': 'Ground', 'Ground': 'Water', 'Flying': 'Electric',
            'Psychic': 'Dark', 'Bug': 'Fire', 'Rock': 'Water',
            'Ghost': 'Dark', 'Dragon': 'Fairy', 'Dark': 'Fairy',
            'Steel': 'Fire', 'Fairy': 'Steel'
        }
        return counter_map.get(target_type)
    
    def _get_fast_counters(self, threats: List[str]) -> List[str]:
        threat_speeds = []
        for name in threats[:5]:
            p = self.db.get_pokemon_by_name(name)
            if p:
                threat_speeds.append(p.get('speed', 100))
        
        avg_threat_speed = sum(threat_speeds) / len(threat_speeds) if threat_speeds else 100
        
        all_pokemon = self.db.get_all_pokemon('gen9vgc2026regf', limit=50)
        fast_pokemon = [p for p in all_pokemon if p.get('speed', 0) > avg_threat_speed]
        
        fast_pokemon.sort(key=lambda x: x.get('speed', 0), reverse=True)
        
        return [p['name'] for p in fast_pokemon[:10]]
    
    def _generate_ai_counter_analysis(self, meta_analysis: Dict, 
                                      counter_teams: List[Dict],
                                      threat_weaknesses: Dict) -> Dict:
        try:
            threats_text = "\n".join([
                f"- {name}: 弱点 {', '.join(weaknesses[:3])}" 
                for name, weaknesses in list(threat_weaknesses.items())[:5]
            ])
            
            teams_text = "\n\n".join([
                f"队伍: {team['name']}\n成员: {', '.join(team['members_zh'])}\n策略: {team['strategy']}"
                for team in counter_teams
            ])
            
            prompt = f"""作为宝可梦VGC对战专家，请分析以下环境威胁并提供克制策略。

## 当前环境威胁
{threats_text}

## 推荐的克制队伍
{teams_text}

## 请提供
1. 对战这些热门威胁的核心思路
2. 每个克制队伍的具体使用建议
3. 需要注意的对局细节
4. 可能的反制风险

请以简洁的战术分析格式返回。"""
            
            api_key = os.getenv('KIMI_API_KEY', 'sk-kimi-TMzmu8ann5Q4DhnRRyY9Vkd22dSgkLivrjmejRIcIGp7kqT6Z9lIp22jvU9hYmjJ')
            base_url = os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "kimi-k2-5",
                    "messages": [
                        {"role": "system", "content": "你是宝可梦VGC对战专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['choices'][0]['message']['content']
                return {
                    'status': 'success',
                    'analysis': analysis
                }
            else:
                return {
                    'status': 'api_error',
                    'error': f"API返回错误: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _save_counter_recommendation(self, result: Dict):
        output_file = Path(__file__).parent / "data" / "counter_recommendations.json"
        
        try:
            existing = []
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            
            existing.append(result)
            existing = existing[-10:]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存克制推荐失败: {e}")


class AutoUpdater:
    def __init__(self):
        self.rule_checker = TavilyRuleChecker()
        self.data_updater = PikalyticsDataUpdater()
        self.meta_analyzer = MetaAnalyzer()
        self.counter_recommender = CounterTeamRecommender()
        
    def run_full_update(self) -> Dict:
        logger.info("=" * 60)
        logger.info("开始执行自动更新流程")
        logger.info("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'regulation_check': None,
            'data_update': None,
            'meta_analysis': None,
            'counter_recommendation': None
        }
        
        try:
            logger.info("\n[1/4] 检查VGC规则更新...")
            has_update, msg, reg_info = self.rule_checker.check_regulation_update()
            results['regulation_check'] = {
                'has_update': has_update,
                'message': msg,
                'regulation_info': reg_info.to_dict()
            }
            logger.info(msg)
        except Exception as e:
            logger.error(f"规则检查失败: {e}")
            results['regulation_check'] = {'error': str(e)}
        
        try:
            logger.info("\n[2/4] 更新Pikalytics数据...")
            self.data_updater.init_history_db()
            stats = self.data_updater.update_all_data(limit=30)
            results['data_update'] = stats
            logger.info(f"数据更新: {stats['updated']} 成功, {stats['failed']} 失败")
        except Exception as e:
            logger.error(f"数据更新失败: {e}")
            results['data_update'] = {'error': str(e)}
        
        try:
            logger.info("\n[3/4] 分析当前环境...")
            meta_analysis = self.meta_analyzer.analyze_current_meta()
            results['meta_analysis'] = {
                'summary': meta_analysis['summary'],
                'top_pokemon_count': len(meta_analysis['top_pokemon']),
                'core_combinations_count': len(meta_analysis['core_combinations'])
            }
            logger.info(f"环境分析完成: {meta_analysis['summary']}")
        except Exception as e:
            logger.error(f"环境分析失败: {e}")
            results['meta_analysis'] = {'error': str(e)}
        
        try:
            logger.info("\n[4/4] 生成克制队伍推荐...")
            counter_result = self.counter_recommender.generate_counter_teams(meta_analysis)
            results['counter_recommendation'] = {
                'teams_generated': len(counter_result['recommended_counter_teams']),
                'ai_status': counter_result['ai_analysis']['status']
            }
            logger.info(f"克制推荐完成: 生成 {len(counter_result['recommended_counter_teams'])} 支队伍")
        except Exception as e:
            logger.error(f"克制推荐失败: {e}")
            results['counter_recommendation'] = {'error': str(e)}
        
        logger.info("\n" + "=" * 60)
        logger.info("自动更新流程执行完毕")
        logger.info("=" * 60)
        
        return results


def main():
    updater = AutoUpdater()
    results = updater.run_full_update()
    
    output_file = Path(__file__).parent / "data" / "last_update_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n更新结果摘要:")
    print(f"- 规则检查: {results['regulation_check'].get('message', 'N/A')}")
    print(f"- 数据更新: {results['data_update'].get('updated', 0)} 成功")
    print(f"- 环境分析: {results['meta_analysis'].get('summary', 'N/A')}")
    print(f"- 克制推荐: {results['counter_recommendation'].get('teams_generated', 0)} 支队伍")


if __name__ == '__main__':
    main()
