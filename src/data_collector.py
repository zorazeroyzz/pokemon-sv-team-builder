# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 数据采集模块
从 Pikalytics 获取 VGC 数据
"""
import requests
import re
import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PokemonData:
    """宝可梦数据结构"""
    name: str
    name_zh: str = ""
    type1: str = ""
    type2: str = ""
    hp: int = 0
    attack: int = 0
    defense: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    speed: int = 0
    bst: int = 0
    usage_rate: float = 0.0


class PikalyticsCollector:
    """Pikalytics 数据采集器"""
    
    BASE_URL = "https://www.pikalytics.com/ai/pokedex"
    FORMAT = "gen9vgc2026regf"
    
    # 热门宝可梦列表（VGC 2026 Regulation F 前50）
    TOP_POKEMON = [
        "Urshifu-Rapid-Strike", "Flutter Mane", "Incineroar", "Tornadus", "Raging Bolt",
        "Ogerpon-Hearthflame", "Chien-Pao", "Ogerpon-Wellspring", "Rillaboom", "Landorus",
        "Gholdengo", "Indeedee-F", "Amoonguss", "Urshifu", "Farigiraf",
        "Dragonite", "Ursaluna", "Dondozo", "Iron Crown", "Tatsugiri",
        "Whimsicott", "Regidrago", "Chi-Yu", "Landorus-Therian", "Ogerpon-Cornerstone",
        "Gouging Fire", "Torkoal", "Glimmora", "Ting-Lu", "Ninetales-Alola",
        "Roaring Moon", "Weezing-Galar", "Cresselia", "Porygon2", "Arcanine-Hisui",
        "Heatran", "Ursaluna-Bloodmoon", "Smeargle", "Archaludon", "Pelipper",
        "Iron Hands", "Thundurus", "Sinistcha", "Entei", "Articuno",
        "Kingambit", "Grimmsnarl", "Moltres-Galar", "Hatterene", "Basculegion"
    ]
    
    # 常用道具列表
    COMMON_ITEMS = [
        "Focus Sash", "Life Orb", "Choice Scarf", "Choice Band", "Choice Specs",
        "Leftovers", "Assault Vest", "Eviolite", "Mental Herb", "White Herb",
        "Safety Goggles", "Covert Cloak", "Booster Energy", "Loaded Dice",
        "Rocky Helmet", "Sitrus Berry", "Lum Berry", "Tera Orb",
        "Mystic Water", "Charcoal", "Miracle Seed", "Magnet", "Never-Melt Ice",
        "Black Glasses", "Black Belt", "Dragon Fang", "Hard Stone", "Soft Sand"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_pokemon_data(self, pokemon_name: str) -> Optional[Dict]:
        """获取单个宝可梦的详细数据"""
        url = f"{self.BASE_URL}/{self.FORMAT}/{pokemon_name}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return self._parse_markdown_data(response.text, pokemon_name)
        except Exception as e:
            print(f"⚠️ 获取 {pokemon_name} 数据失败: {e}")
            return None
    
    def _parse_markdown_data(self, markdown_text: str, pokemon_name: str) -> Dict:
        """解析 Markdown 格式的数据"""
        data = {
            'name': pokemon_name,
            'name_zh': '',
            'type1': '',
            'type2': '',
            'hp': 0, 'attack': 0, 'defense': 0,
            'sp_attack': 0, 'sp_defense': 0, 'speed': 0, 'bst': 0,
            'usage_rate': 0,
            'moves': [],
            'items': [],
            'teammates': [],
            'abilities': []
        }
        
        # 解析基础数值
        stat_pattern = r'\|\s*(HP|Attack|Defense|Sp\. Atk|Sp\. Def|Speed)\s*\|\s*(\d+)\s*\|'
        stats = re.findall(stat_pattern, markdown_text)
        stat_map = {
            'HP': 'hp', 'Attack': 'attack', 'Defense': 'defense',
            'Sp. Atk': 'sp_attack', 'Sp. Def': 'sp_defense', 'Speed': 'speed'
        }
        for stat_name, stat_value in stats:
            if stat_name in stat_map:
                data[stat_map[stat_name]] = int(stat_value)
        
        # 计算种族值总和
        data['bst'] = sum([
            data['hp'], data['attack'], data['defense'],
            data['sp_attack'], data['sp_defense'], data['speed']
        ])
        
        # 解析技能及使用率
        move_pattern = r'[-*]\s*\*\*(.+?)\*\*:\s*(\d+\.?\d*)%'
        moves = re.findall(move_pattern, markdown_text)
        for move_name, usage in moves:
            data['moves'].append({
                'name': move_name.strip(),
                'usage_rate': float(usage)
            })
        
        # 解析道具及使用率
        item_section = re.search(r'## Common Items\n(.+?)(?=##|\Z)', markdown_text, re.DOTALL)
        if item_section:
            items_text = item_section.group(1)
            items = re.findall(move_pattern, items_text)
            for item_name, usage in items:
                data['items'].append({
                    'name': item_name.strip(),
                    'usage_rate': float(usage)
                })
        
        # 解析队友及协同率
        teammate_section = re.search(r'## Common Teammates\n(.+?)(?=##|\Z)', markdown_text, re.DOTALL)
        if teammate_section:
            teammates_text = teammate_section.group(1)
            teammates = re.findall(move_pattern, teammates_text)
            for teammate_name, synergy in teammates:
                data['teammates'].append({
                    'name': teammate_name.strip(),
                    'synergy_rate': float(synergy)
                })
        
        # 解析特性
        ability_pattern = r'[-*]\s*\*\*(.+?)\*\*:\s*(\d+\.?\d*)%'
        ability_section = re.search(r'## Common Abilities\n(.+?)(?=##|\Z)', markdown_text, re.DOTALL)
        if ability_section:
            abilities_text = ability_section.group(1)
            abilities = re.findall(ability_pattern, abilities_text)
            for ability_name, usage in abilities:
                data['abilities'].append({
                    'name': ability_name.strip(),
                    'usage_rate': float(usage)
                })
        
        return data
    
    def collect_all_data(self, db, limit: int = None):
        """采集所有宝可梦数据"""
        pokemon_list = self.TOP_POKEMON[:limit] if limit else self.TOP_POKEMON
        
        print(f"🔄 开始采集 {len(pokemon_list)} 只宝可梦的数据...")
        
        for i, pokemon_name in enumerate(pokemon_list, 1):
            print(f"  [{i}/{len(pokemon_list)}] 采集 {pokemon_name}...", end=" ")
            
            data = self.fetch_pokemon_data(pokemon_name)
            if data:
                # 插入宝可梦基础数据
                db.insert_pokemon({
                    'name': data['name'],
                    'name_zh': data['name_zh'],
                    'type1': data['type1'] or 'Normal',
                    'type2': data['type2'],
                    'hp': data['hp'],
                    'attack': data['attack'],
                    'defense': data['defense'],
                    'sp_attack': data['sp_attack'],
                    'sp_defense': data['sp_defense'],
                    'speed': data['speed'],
                    'bst': data['bst'],
                    'usage_rate': data['usage_rate'],
                    'format': self.FORMAT
                })
                
                # 插入技能数据
                for move in data['moves']:
                    db.insert_move({'name': move['name']})
                    db.insert_pokemon_move(
                        data['name'],
                        move['name'],
                        move['usage_rate'],
                        self.FORMAT
                    )
                
                # 插入道具数据
                for item in data['items']:
                    db.insert_item({'name': item['name']})
                    db.insert_pokemon_item(
                        data['name'],
                        item['name'],
                        item['usage_rate'],
                        self.FORMAT
                    )
                
                # 插入队友数据
                for teammate in data['teammates']:
                    db.insert_pokemon_teammate(
                        data['name'],
                        teammate['name'],
                        teammate['synergy_rate'],
                        self.FORMAT
                    )
                
                print("✅")
            else:
                print("❌")
            
            # 添加延迟避免请求过快
            time.sleep(0.5)
        
        print(f"✅ 数据采集完成！")
    
    def get_usage_tiers(self) -> Dict[str, List[str]]:
        """获取使用率的层级分类"""
        return {
            'S_tier': self.TOP_POKEMON[:5],      # 45%+
            'A_tier': self.TOP_POKEMON[5:15],    # 15-30%
            'B_tier': self.TOP_POKEMON[15:30],   # 5-15%
            'C_tier': self.TOP_POKEMON[30:50]    # 1-5%
        }


# 宝可梦中文名称映射（部分常见宝可梦）
POKEMON_NAME_ZH = {
    "Urshifu-Rapid-Strike": "武道熊师（连击流）",
    "Flutter Mane": "振翼发",
    "Incineroar": "炽焰咆哮虎",
    "Tornadus": "龙卷云",
    "Raging Bolt": "猛雷鼓",
    "Ogerpon-Hearthflame": "厄诡椪（火灶）",
    "Chien-Pao": "古剑豹",
    "Ogerpon-Wellspring": "厄诡椪（水井）",
    "Rillaboom": "轰擂金刚猩",
    "Landorus": "土地云",
    "Gholdengo": "赛富豪",
    "Indeedee-F": "爱管侍（雌性）",
    "Amoonguss": "败露球菇",
    "Urshifu": "武道熊师（一击流）",
    "Farigiraf": "奇麒麟",
    "Dragonite": "快龙",
    "Ursaluna": "月月熊",
    "Dondozo": "吃吼霸",
    "Iron Crown": "铁头壳",
    "Tatsugiri": "米立龙",
    "Whimsicott": "风妖精",
    "Regidrago": "雷吉铎拉戈",
    "Chi-Yu": "古玉鱼",
    "Landorus-Therian": "土地云（灵兽）",
    "Ogerpon-Cornerstone": "厄诡椪（础石）",
    "Gouging Fire": "破空焰",
    "Torkoal": "煤炭龟",
    "Glimmora": "晶光花",
    "Ting-Lu": "古鼎鹿",
    "Ninetales-Alola": "九尾（阿罗拉）",
    "Roaring Moon": "轰鸣月",
    "Weezing-Galar": "双弹瓦斯（伽勒尔）",
    "Cresselia": "克雷色利亚",
    "Porygon2": "多边兽2型",
    "Arcanine-Hisui": "风速狗（洗翠）",
    "Heatran": "席多蓝恩",
    "Ursaluna-Bloodmoon": "月月熊（血月）",
    "Smeargle": "图图犬",
    "Archaludon": "铝钢桥龙",
    "Pelipper": "大嘴鸥",
    "Iron Hands": "铁臂膀",
    "Thundurus": "雷电云",
    "Sinistcha": "来悲粗茶",
    "Entei": "炎帝",
    "Articuno": "急冻鸟",
    "Kingambit": "仆刀将军",
    "Grimmsnarl": "长毛巨魔",
    "Moltres-Galar": "火焰鸟（伽勒尔）",
    "Hatterene": "布莉姆温",
    "Basculegion": "幽尾玄鱼"
}
