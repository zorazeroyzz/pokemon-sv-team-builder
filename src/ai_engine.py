# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - AI 推荐引擎
使用 LongCat 本地筛选 + Kimi 2.5 深度推荐
"""
import os
import json
from typing import List, Dict, Optional


class LongCatFilter:
    """
    LongCat 本地筛选器
    基于规则和数据进行初步筛选
    """
    
    def __init__(self, db, type_calc):
        self.db = db
        self.type_calc = type_calc
    
    def filter_candidates(self, candidates: List[List[str]], 
                          style: str,
                          min_score: float = 5.0) -> List[Dict]:
        """
        本地筛选候选队伍
        """
        filtered = []
        
        for team in candidates:
            # 基础数据验证
            if len(team) != 6:
                continue
            
            # 检查重复
            if len(set(team)) != 6:
                continue
            
            # 获取宝可梦数据
            pokemon_data = []
            valid = True
            for name in team:
                p = self.db.get_pokemon_by_name(name)
                if not p:
                    valid = False
                    break
                pokemon_data.append(p)
            
            if not valid:
                continue
            
            # 计算基础分数
            score = self._calculate_base_score(team, pokemon_data, style)
            
            if score >= min_score:
                filtered.append({
                    'team': team,
                    'pokemon_data': pokemon_data,
                    'base_score': score,
                    'features': self._extract_features(team, pokemon_data)
                })
        
        # 按分数排序
        filtered.sort(key=lambda x: x['base_score'], reverse=True)
        return filtered[:10]  # 返回前10个
    
    def _calculate_base_score(self, team: List[str], 
                              pokemon_data: List[Dict],
                              style: str) -> float:
        """计算基础分数"""
        score = 5.0  # 基础分
        
        # 使用率加分
        total_usage = sum(p.get('usage_rate', 0) for p in pokemon_data)
        score += min(total_usage / 100, 3)  # 最高3分
        
        # 属性多样性加分
        types = set()
        for p in pokemon_data:
            types.add(p['type1'])
            if p['type2']:
                types.add(p['type2'])
        score += len(types) * 0.2
        
        # 风格匹配
        if style == 'offensive':
            avg_offense = sum(p.get('attack', 0) + p.get('sp_attack', 0) for p in pokemon_data) / 6
            score += avg_offense / 100
        elif style == 'defensive':
            avg_defense = sum(p.get('hp', 0) + p.get('defense', 0) + p.get('sp_defense', 0) for p in pokemon_data) / 6
            score += avg_defense / 150
        
        return score
    
    def _extract_features(self, team: List[str], pokemon_data: List[Dict]) -> Dict:
        """提取队伍特征"""
        features = {
            'types': [],
            'avg_bst': 0,
            'avg_usage': 0,
            'roles': []
        }
        
        for p in pokemon_data:
            features['types'].append({
                'name': p['name'],
                'type1': p['type1'],
                'type2': p['type2']
            })
            features['avg_bst'] += p.get('bst', 0)
            features['avg_usage'] += p.get('usage_rate', 0)
            
            # 简单角色判断
            if p.get('attack', 0) > 120 or p.get('sp_attack', 0) > 120:
                features['roles'].append(f"{p['name']}: 输出手")
            elif p.get('defense', 0) > 100 and p.get('sp_defense', 0) > 100:
                features['roles'].append(f"{p['name']}: 坦克")
            elif p.get('speed', 0) > 110:
                features['roles'].append(f"{p['name']}: 高速")
        
        features['avg_bst'] /= len(pokemon_data)
        features['avg_usage'] /= len(pokemon_data)
        
        return features


class KimiRecommender:
    """
    Kimi 2.5 深度推荐引擎
    使用 AI 进行深度分析和推荐
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk-kimi-TMzmu8ann5Q4DhnRRyY9Vkd22dSgkLivrjmejRIcIGp7kqT6Z9lIp22jvU9hYmjJ"
        self.base_url = os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')
        self.model = os.getenv('KIMI_MODEL', 'kimi-k2-5')
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk-kimi-TMzmu8ann5Q4DhnRRyY9Vkd22dSgkLivrjmejRIcIGp7kqT6Z9lIp22jvU9hYmjJ"
        self.base_url = "https://api.kimi.com/coding"
        self.model = "kimi-k2.5"
    
    def generate_team_recommendation(self, 
                                     filtered_teams: List[Dict],
                                     style: str) -> Dict:
        """
        使用 Kimi 生成队伍推荐
        """
        try:
            from anthropic import Anthropic
            
            client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 构建提示
            prompt = self._build_prompt(filtered_teams, style)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                system="你是宝可梦VGC对战专家，擅长队伍构建和战术分析。",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析响应
            recommendation = self._parse_response(response.content[0].text)
            return recommendation
            
        except Exception as e:
            print(f"⚠️ Kimi API 调用失败: {e}")
            # 返回最佳本地筛选结果
            return self._fallback_recommendation(filtered_teams[0] if filtered_teams else None, style)
    
    def _build_prompt(self, teams: List[Dict], style: str) -> str:
        """构建提示词"""
        style_desc = {
            'balanced': '平衡型（攻守兼备）',
            'offensive': '进攻型（高火力压制）',
            'defensive': '防守型（高耐久消耗）'
        }
        
        prompt = f"""请作为宝可梦VGC对战专家，从以下候选队伍中选择并推荐一个最优的{style_desc.get(style, '平衡型')}队伍。

## 候选队伍数据

"""
        
        for i, team_data in enumerate(teams[:5], 1):
            team = team_data['team']
            features = team_data['features']
            
            prompt += f"\n### 候选队伍 {i}\n"
            prompt += f"成员: {', '.join(team)}\n"
            prompt += f"基础评分: {team_data['base_score']:.2f}\n"
            prompt += f"平均种族值: {features['avg_bst']:.0f}\n"
            prompt += f"平均使用率: {features['avg_usage']:.1f}%\n"
            prompt += "角色分布:\n"
            for role in features['roles']:
                prompt += f"  - {role}\n"
        
        prompt += """
## 请提供以下分析

1. **推荐队伍**: 从候选中选择最佳的6只宝可梦
2. **每只宝可梦的配招**: 4个技能
3. **每只宝可梦的道具**: 1个道具
4. **每只宝可梦的性格**: 推荐性格
5. **队伍战术思路**: 整体打法说明
6. **对战要点**: 关键对局策略

请以JSON格式返回：

```json
{
  "team": ["宝可梦1", "宝可梦2", "宝可梦3", "宝可梦4", "宝可梦5", "宝可梦6"],
  "members": [
    {
      "name": "宝可梦1",
      "moves": ["技能1", "技能2", "技能3", "技能4"],
      "item": "道具",
      "nature": "性格",
      "role": "角色定位"
    }
  ],
  "strategy": "整体战术思路",
  "tips": "对战要点"
}
```
"""
        return prompt
    
    def _parse_response(self, content: str) -> Dict:
        """解析 Kimi 响应"""
        # 尝试提取 JSON
        import re
        
        # 查找 JSON 代码块
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 查找任意 JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # 返回原始内容
        return {
            'raw_response': content,
            'team': [],
            'strategy': '解析失败'
        }
    
    def _fallback_recommendation(self, team_data: Dict, style: str) -> Dict:
        """备用推荐（当 API 失败时）"""
        if not team_data:
            return {
                'team': [],
                'strategy': '无可用数据',
                'error': '筛选结果为空'
            }
        
        team = team_data['team']
        
        # 生成基础配招和道具
        members = []
        for name in team:
            members.append({
                'name': name,
                'moves': ['根据对战环境选择', '根据对战环境选择', '根据对战环境选择', '守住'],
                'item': '根据战术选择',
                'nature': '根据build选择',
                'role': '待分析'
            })
        
        return {
            'team': team,
            'members': members,
            'strategy': f'{style}型队伍，基于热门宝可梦组合',
            'tips': '请参考 Pikalytics 获取详细配招',
            'note': 'AI 推荐服务暂时不可用，显示为基础推荐'
        }


class AIEngine:
    """
    AI 推荐引擎主类
    整合 LongCat 筛选和 Kimi 推荐
    """
    
    def __init__(self, db, type_calc, api_key: str = None):
        self.filter = LongCatFilter(db, type_calc)
        self.recommender = KimiRecommender(api_key)
    
    def recommend_team(self, candidates: List[List[str]], 
                       style: str = 'balanced') -> Dict:
        """
        完整的推荐流程
        """
        print("🔍 LongCat 本地筛选中...")
        filtered = self.filter.filter_candidates(candidates, style)
        
        if not filtered:
            return {
                'error': '没有通过筛选的候选队伍',
                'team': [],
                'strategy': ''
            }
        
        print(f"✅ 筛选出 {len(filtered)} 个候选队伍")
        print("🤖 Kimi 深度分析中...")
        
        recommendation = self.recommender.generate_team_recommendation(filtered, style)
        
        return recommendation
