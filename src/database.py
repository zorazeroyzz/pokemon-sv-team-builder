# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 数据库模块
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class PokemonDatabase:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "pokemon.db"
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_tables(self):
        """初始化数据库表结构"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 宝可梦基础信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_zh TEXT,
                type1 TEXT NOT NULL,
                type2 TEXT,
                hp INTEGER,
                attack INTEGER,
                defense INTEGER,
                sp_attack INTEGER,
                sp_defense INTEGER,
                speed INTEGER,
                bst INTEGER,
                usage_rate REAL,
                format TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 技能表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_zh TEXT,
                type TEXT,
                category TEXT,
                power INTEGER,
                accuracy INTEGER,
                pp INTEGER,
                description TEXT
            )
        ''')
        
        # 道具表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_zh TEXT,
                description TEXT,
                category TEXT
            )
        ''')
        
        # 宝可梦-技能关联表（使用率数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon_moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_name TEXT NOT NULL,
                move_name TEXT NOT NULL,
                usage_rate REAL,
                format TEXT,
                FOREIGN KEY (pokemon_name) REFERENCES pokemon(name),
                FOREIGN KEY (move_name) REFERENCES moves(name),
                UNIQUE(pokemon_name, move_name, format)
            )
        ''')
        
        # 宝可梦-道具关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                usage_rate REAL,
                format TEXT,
                FOREIGN KEY (pokemon_name) REFERENCES pokemon(name),
                FOREIGN KEY (item_name) REFERENCES items(name),
                UNIQUE(pokemon_name, item_name, format)
            )
        ''')
        
        # 宝可梦队友关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon_teammates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_name TEXT NOT NULL,
                teammate_name TEXT NOT NULL,
                synergy_rate REAL,
                format TEXT,
                FOREIGN KEY (pokemon_name) REFERENCES pokemon(name),
                FOREIGN KEY (teammate_name) REFERENCES pokemon(name),
                UNIQUE(pokemon_name, teammate_name, format)
            )
        ''')
        
        # 推荐队伍表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommended_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                style TEXT,
                pokemon_list TEXT,  -- JSON格式存储6只宝可梦
                strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        self.close()
        print("✅ 数据库表初始化完成")
    
    def insert_pokemon(self, pokemon_data: Dict):
        """插入宝可梦数据"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pokemon 
            (name, name_zh, type1, type2, hp, attack, defense, sp_attack, sp_defense, speed, bst, usage_rate, format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pokemon_data['name'],
            pokemon_data.get('name_zh', ''),
            pokemon_data['type1'],
            pokemon_data.get('type2'),
            pokemon_data.get('hp', 0),
            pokemon_data.get('attack', 0),
            pokemon_data.get('defense', 0),
            pokemon_data.get('sp_attack', 0),
            pokemon_data.get('sp_defense', 0),
            pokemon_data.get('speed', 0),
            pokemon_data.get('bst', 0),
            pokemon_data.get('usage_rate', 0),
            pokemon_data.get('format', 'gen9vgc2026regf')
        ))
        
        conn.commit()
        self.close()
    
    def insert_move(self, move_data: Dict):
        """插入技能数据"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO moves (name, name_zh, type, category, power, accuracy, pp, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            move_data['name'],
            move_data.get('name_zh', ''),
            move_data.get('type', ''),
            move_data.get('category', ''),
            move_data.get('power'),
            move_data.get('accuracy'),
            move_data.get('pp'),
            move_data.get('description', '')
        ))
        
        conn.commit()
        self.close()
    
    def insert_item(self, item_data: Dict):
        """插入道具数据"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO items (name, name_zh, description, category)
            VALUES (?, ?, ?, ?)
        ''', (
            item_data['name'],
            item_data.get('name_zh', ''),
            item_data.get('description', ''),
            item_data.get('category', '')
        ))
        
        conn.commit()
        self.close()
    
    def insert_pokemon_move(self, pokemon_name: str, move_name: str, usage_rate: float, format_name: str):
        """插入宝可梦-技能关联"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pokemon_moves (pokemon_name, move_name, usage_rate, format)
            VALUES (?, ?, ?, ?)
        ''', (pokemon_name, move_name, usage_rate, format_name))
        
        conn.commit()
        self.close()
    
    def insert_pokemon_item(self, pokemon_name: str, item_name: str, usage_rate: float, format_name: str):
        """插入宝可梦-道具关联"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pokemon_items (pokemon_name, item_name, usage_rate, format)
            VALUES (?, ?, ?, ?)
        ''', (pokemon_name, item_name, usage_rate, format_name))
        
        conn.commit()
        self.close()
    
    def insert_pokemon_teammate(self, pokemon_name: str, teammate_name: str, synergy_rate: float, format_name: str):
        """插入宝可梦-队友关联"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pokemon_teammates (pokemon_name, teammate_name, synergy_rate, format)
            VALUES (?, ?, ?, ?)
        ''', (pokemon_name, teammate_name, synergy_rate, format_name))
        
        conn.commit()
        self.close()
    
    def get_pokemon_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取宝可梦信息"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pokemon WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        self.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_pokemon(self, format_name: str = None, limit: int = None) -> List[Dict]:
        """获取所有宝可梦列表"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if format_name:
            cursor.execute(
                'SELECT * FROM pokemon WHERE format = ? ORDER BY usage_rate DESC',
                (format_name,)
            )
        else:
            cursor.execute('SELECT * FROM pokemon ORDER BY usage_rate DESC')
        
        rows = cursor.fetchall()
        self.close()
        
        result = [dict(row) for row in rows]
        if limit:
            result = result[:limit]
        return result
    
    def get_pokemon_moves(self, pokemon_name: str, format_name: str = None, limit: int = 6) -> List[Dict]:
        """获取宝可梦的技能列表"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if format_name:
            cursor.execute('''
                SELECT pm.*, m.type, m.category, m.power 
                FROM pokemon_moves pm
                JOIN moves m ON pm.move_name = m.name
                WHERE pm.pokemon_name = ? AND pm.format = ?
                ORDER BY pm.usage_rate DESC
            ''', (pokemon_name, format_name))
        else:
            cursor.execute('''
                SELECT pm.*, m.type, m.category, m.power 
                FROM pokemon_moves pm
                JOIN moves m ON pm.move_name = m.name
                WHERE pm.pokemon_name = ?
                ORDER BY pm.usage_rate DESC
            ''', (pokemon_name,))
        
        rows = cursor.fetchall()
        self.close()
        
        result = [dict(row) for row in rows]
        if limit:
            result = result[:limit]
        return result
    
    def get_pokemon_items(self, pokemon_name: str, format_name: str = None, limit: int = 5) -> List[Dict]:
        """获取宝可梦的道具列表"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if format_name:
            cursor.execute('''
                SELECT pi.*, i.description
                FROM pokemon_items pi
                JOIN items i ON pi.item_name = i.name
                WHERE pi.pokemon_name = ? AND pi.format = ?
                ORDER BY pi.usage_rate DESC
            ''', (pokemon_name, format_name))
        else:
            cursor.execute('''
                SELECT pi.*, i.description
                FROM pokemon_items pi
                JOIN items i ON pi.item_name = i.name
                WHERE pi.pokemon_name = ?
                ORDER BY pi.usage_rate DESC
            ''', (pokemon_name,))
        
        rows = cursor.fetchall()
        self.close()
        
        result = [dict(row) for row in rows]
        if limit:
            result = result[:limit]
        return result
    
    def get_pokemon_teammates(self, pokemon_name: str, format_name: str = None, limit: int = 10) -> List[Dict]:
        """获取宝可梦的队友列表"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if format_name:
            cursor.execute('''
                SELECT pt.*, p.type1, p.type2
                FROM pokemon_teammates pt
                JOIN pokemon p ON pt.teammate_name = p.name
                WHERE pt.pokemon_name = ? AND pt.format = ?
                ORDER BY pt.synergy_rate DESC
            ''', (pokemon_name, format_name))
        else:
            cursor.execute('''
                SELECT pt.*, p.type1, p.type2
                FROM pokemon_teammates pt
                JOIN pokemon p ON pt.teammate_name = p.name
                WHERE pt.pokemon_name = ?
                ORDER BY pt.synergy_rate DESC
            ''', (pokemon_name,))
        
        rows = cursor.fetchall()
        self.close()
        
        result = [dict(row) for row in rows]
        if limit:
            result = result[:limit]
        return result
    
    def save_recommended_team(self, team_data: Dict):
        """保存推荐的队伍"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recommended_teams (team_name, style, pokemon_list, strategy)
            VALUES (?, ?, ?, ?)
        ''', (
            team_data.get('team_name', ''),
            team_data.get('style', ''),
            json.dumps(team_data.get('pokemon_list', [])),
            team_data.get('strategy', '')
        ))
        
        conn.commit()
        self.close()
