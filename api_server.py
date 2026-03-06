#!/usr/bin/env python3
"""
宝可梦VGC队伍推荐API服务器
提供队伍推荐、分析等功能的REST API
"""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 添加recommender模块路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "recommender"))
from pokemon_recommender import PokemonRecommender

class TeamRecommenderHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.recommender = PokemonRecommender(
            db_path=str(Path(__file__).parent / "data" / "pokemon.db")
        )
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/api/recommend':
            strategy = query.get('strategy', ['balanced'])[0]
            team = self.recommender.recommend_team(strategy)
            self._send_json_response(team)
        
        elif path == '/api/analyze':
            team_names = query.get('team', [])
            if team_names:
                analysis = self.recommender.analyze_team(team_names)
                self._send_json_response(analysis)
            else:
                self._send_error_response(400, "Missing team parameter")
        
        elif path == '/api/strategies':
            strategies = [
                {"id": "balanced", "name": "平衡队", "description": "攻守兼备的通用队伍"},
                {"id": "offensive", "name": "进攻队", "description": "高速高攻的速攻队伍"},
                {"id": "defensive", "name": "防守队", "description": "高耐久消耗型队伍"},
                {"id": "trick-room", "name": "戏法空间队", "description": "低速高攻的空间队伍"}
            ]
            self._send_json_response(strategies)
        
        else:
            self._send_error_response(404, "Not found")
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                team_names = data.get('team', [])
                analysis = self.recommender.analyze_team(team_names)
                self._send_json_response(analysis)
            except json.JSONDecodeError:
                self._send_error_response(400, "Invalid JSON")
        
        else:
            self._send_error_response(404, "Not found")
    
    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))
    
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run_api_server(port=8081):
    server = HTTPServer(('0.0.0.0', port), TeamRecommenderHandler)
    print(f"🎮 宝可梦VGC队伍推荐API服务器已启动!")
    print(f"📍 API地址: http://0.0.0.0:{port}")
    print(f"\n可用接口:")
    print(f"  GET  /api/recommend?strategy=balanced")
    print(f"  GET  /api/analyze?team=pokemon1&team=pokemon2")
    print(f"  GET  /api/strategies")
    print(f"  POST /api/analyze (JSON body: {{\"team\": [\"pokemon1\", ...]}})")
    print(f"\n按 Ctrl+C 停止服务器\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='宝可梦VGC队伍推荐API服务器')
    parser.add_argument('--port', type=int, default=8081, help='服务器端口 (默认: 8081)')
    args = parser.parse_args()
    
    run_api_server(args.port)
