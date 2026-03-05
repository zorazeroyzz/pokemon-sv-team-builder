# -*- coding: utf-8 -*-
"""
宝可梦朱紫队伍推荐系统 - 默认配招数据
基于 VGC 2026 Regulation F 常见配置
"""

# 热门宝可梦的推荐配招、道具、性格
DEFAULT_SETS = {
    "Urshifu-Rapid-Strike": {
        "moves": ["水流连打", "近身战", "水流喷射", "看穿/守住"],
        "items": ["神秘水滴", "气势披带", "讲究围巾"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Flutter Mane": {
        "moves": ["暗影球", "魔法闪耀", "月亮之力", "守住/同命"],
        "items": ["气势披带", "命玉", "讲究眼镜"],
        "natures": ["胆小", "内敛"],
        "role": "特攻输出手"
    },
    "Incineroar": {
        "moves": ["闪焰冲锋", "DD金钩臂", "击掌奇袭", "鬼火/大声咆哮"],
        "items": ["气势披带", "讲究头带", "突击背心"],
        "natures": ["固执", "勇敢"],
        "role": "威吓手/辅助"
    },
    "Tornadus": {
        "moves": ["暴风", "顺风", "挑衅", "守住/虫鸣"],
        "items": ["气势披带", "讲究围巾", "命玉"],
        "natures": ["胆小", "爽朗"],
        "role": "顺风手/控速"
    },
    "Raging Bolt": {
        "moves": ["电光束", "龙星群", "流星群", "守住/十万伏特"],
        "items": ["讲究眼镜", "命玉", "气势披带"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Ogerpon-Hearthflame": {
        "moves": ["棘藤棒", "木角", "剑舞", "守住/突袭"],
        "items": ["火灶面具", "气势披带", "讲究头带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Chien-Pao": {
        "moves": ["冰柱坠击", "突袭", "圣剑", "守住/剑舞"],
        "items": ["气势披带", "讲究头带", "生命玉"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Ogerpon-Wellspring": {
        "moves": ["棘藤棒", "木角", "剑舞", "守住/突袭"],
        "items": ["水井面具", "气势披带", "讲究头带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Rillaboom": {
        "moves": ["鼓击", "木槌", "击掌奇袭", "守住/急速折返"],
        "items": ["气势披带", "讲究头带", "突击背心"],
        "natures": ["固执", "勇敢"],
        "role": "草场手/物理输出"
    },
    "Landorus": {
        "moves": ["大地之力", "污泥炸弹", "守住", "真气弹/岩崩"],
        "items": ["气势披带", "讲究眼镜", "命玉"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Gholdengo": {
        "moves": ["淘金潮", "暗影球", "真气弹", "守住/戏法"],
        "items": ["气势披带", "讲究眼镜", "命玉"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Indeedee-F": {
        "moves": ["精神强念", "帮助", "守住", "戏法空间/特性互换"],
        "items": ["气势披带", "心灵香草", "气势披带"],
        "natures": ["大胆", "温和"],
        "role": "精神场地/辅助"
    },
    "Amoonguss": {
        "moves": ["蘑菇孢子", "愤怒粉", "守住", "终极吸取/清除之烟"],
        "items": ["气势披带", "黑色污泥", "气势披带"],
        "natures": ["大胆", "悠闲"],
        "role": "控场/辅助"
    },
    "Urshifu": {
        "moves": ["暗冥强击", "近身战", "音速拳", "看穿/守住"],
        "items": ["气势披带", "讲究头带", "气势披带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Farigiraf": {
        "moves": ["精神强念", "暗影球", "戏法空间", "守住/双光束"],
        "items": ["气势披带", "气势披带", "讲究眼镜"],
        "natures": ["内敛", "冷静"],
        "role": "戏法空间手"
    },
    "Dragonite": {
        "moves": ["神速", "龙爪", "火焰拳", "守住/剑舞"],
        "items": ["气势披带", "讲究头带", "气势披带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Ursaluna": {
        "moves": ["硬撑", "地震", "暗影爪", "守住/剑舞"],
        "items": ["火焰珠", "气势披带", "讲究头带"],
        "natures": ["固执", "勇敢"],
        "role": "物理输出手"
    },
    "Dondozo": {
        "moves": ["波动冲", "地震", "咒术", "睡觉/梦话"],
        "items": ["吃剩的东西", "气势披带", "讲究头带"],
        "natures": ["固执", "勇敢"],
        "role": "坦克/强化"
    },
    "Iron Crown": {
        "moves": ["精神强念", "加农光炮", "真气弹", "守住/十万伏特"],
        "items": ["气势披带", "讲究眼镜", "命玉"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Tatsugiri": {
        "moves": ["流星群", "水炮", "冰冻光束", "守住/龙星群"],
        "items": ["气势披带", "讲究眼镜", "气势披带"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Whimsicott": {
        "moves": ["顺风", "挑衅", "帮助", "守住/月亮之力"],
        "items": ["气势披带", "气势披带", "气势披带"],
        "natures": ["胆小", "大胆"],
        "role": "顺风手/辅助"
    },
    "Regidrago": {
        "moves": ["巨龙威能", "流星群", "真气弹", "守住/龙星群"],
        "items": ["气势披带", "讲究眼镜", "气势披带"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Chi-Yu": {
        "moves": ["热风", "恶之波动", "精神强念", "守住/喷射火焰"],
        "items": ["气势披带", "讲究眼镜", "气势披带"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手"
    },
    "Landorus-Therian": {
        "moves": ["地震", "岩崩", "急速折返", "守住/剑舞"],
        "items": ["气势披带", "讲究头带", "气势披带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Ogerpon-Cornerstone": {
        "moves": ["棘藤棒", "木角", "剑舞", "守住/突袭"],
        "items": ["础石面具", "气势披带", "讲究头带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Gouging Fire": {
        "moves": ["火焰牙", "疯狂伏特", "龙爪", "守住/剑舞"],
        "items": ["气势披带", "讲究头带", "气势披带"],
        "natures": ["固执", "爽朗"],
        "role": "物理输出手"
    },
    "Torkoal": {
        "moves": ["喷烟", "热风", "守住", "哈欠/清除之烟"],
        "items": ["气势披带", "气势披带", "讲究眼镜"],
        "natures": ["内敛", "冷静"],
        "role": "晴天手/特攻输出"
    },
    "Glimmora": {
        "moves": ["污泥炸弹", "大地之力", "守住", "撒菱/毒菱"],
        "items": ["气势披带", "气势披带", "气势披带"],
        "natures": ["内敛", "胆小"],
        "role": "特攻输出手/撒钉"
    },
    "Ting-Lu": {
        "moves": ["跺脚", "鬼面", "挑衅", "守住/睡觉"],
        "items": ["吃剩的东西", "气势披带", "气势披带"],
        "natures": ["固执", "勇敢"],
        "role": "坦克/干扰"
    },
    "Ninetales-Alola": {
        "moves": ["暴风雪", "月亮之力", "守住", "冷冻干燥/极光幕"],
        "items": ["气势披带", "气势披带", "讲究眼镜"],
        "natures": ["内敛", "胆小"],
        "role": "雪天手/特攻输出"
    }
}

# 道具中文名称映射
ITEM_NAME_ZH = {
    "Focus Sash": "气势披带",
    "Life Orb": "命玉",
    "Choice Scarf": "讲究围巾",
    "Choice Band": "讲究头带",
    "Choice Specs": "讲究眼镜",
    "Leftovers": "吃剩的东西",
    "Assault Vest": "突击背心",
    "Eviolite": "进化奇石",
    "Mental Herb": "心灵香草",
    "White Herb": "白色香草",
    "Safety Goggles": "防尘护目镜",
    "Covert Cloak": "隐蔽斗篷",
    "Booster Energy": "驱劲能量",
    "Loaded Dice": "机变骰子",
    "Rocky Helmet": "凸凸头盔",
    "Sitrus Berry": "文柚果",
    "Lum Berry": "木子果",
    "Tera Orb": "太晶珠",
    "Mystic Water": "神秘水滴",
    "Charcoal": "木炭",
    "Miracle Seed": "奇迹种子",
    "Magnet": "磁铁",
    "Never-Melt Ice": "不融冰",
    "Black Glasses": "黑色眼镜",
    "Black Belt": "黑带",
    "Dragon Fang": "龙之牙",
    "Hard Stone": "硬石头",
    "Soft Sand": "柔软沙子",
    "Flame Orb": "火焰珠",
    "Toxic Orb": "剧毒珠"
}

# 技能中文名称映射
MOVE_NAME_ZH = {
    "Surging Strikes": "水流连打",
    "Close Combat": "近身战",
    "Aqua Jet": "水流喷射",
    "Detect": "看穿",
    "Protect": "守住",
    "Shadow Ball": "暗影球",
    "Dazzling Gleam": "魔法闪耀",
    "Moonblast": "月亮之力",
    "Destiny Bond": "同命",
    "Fake Out": "击掌奇袭",
    "Flare Blitz": "闪焰冲锋",
    "Knock Off": "DD金钩臂",
    "Will-O-Wisp": "鬼火",
    "Snarl": "大声咆哮",
    "Hurricane": "暴风",
    "Tailwind": "顺风",
    "Taunt": "挑衅",
    "Bug Buzz": "虫鸣",
    "Thunderclap": "电光束",
    "Draco Meteor": "龙星群",
    "Thunderbolt": "十万伏特",
    "Ivy Cudgel": "棘藤棒",
    "Wood Hammer": "木槌",
    "Swords Dance": "剑舞",
    "Sucker Punch": "突袭",
    "Ice Spinner": "冰柱坠击",
    "Sacred Sword": "圣剑",
    "Drum Beating": "鼓击",
    "U-turn": "急速折返",
    "Earth Power": "大地之力",
    "Sludge Bomb": "污泥炸弹",
    "Focus Blast": "真气弹",
    "Rock Slide": "岩崩",
    "Make It Rain": "淘金潮",
    "Trick": "戏法",
    "Psychic": "精神强念",
    "Helping Hand": "帮助",
    "Skill Swap": "特性互换",
    "Spore": "蘑菇孢子",
    "Rage Powder": "愤怒粉",
    "Giga Drain": "终极吸取",
    "Clear Smog": "清除之烟",
    "Wicked Blow": "暗冥强击",
    "Mach Punch": "音速拳",
    "Trick Room": "戏法空间",
    "Twin Beam": "双光束",
    "Extreme Speed": "神速",
    "Dragon Claw": "龙爪",
    "Fire Punch": "火焰拳",
    "Facade": "硬撑",
    "Earthquake": "地震",
    "Shadow Claw": "暗影爪",
    "Wave Crash": "波动冲",
    "Curse": "咒术",
    "Rest": "睡觉",
    "Sleep Talk": "梦话",
    "Flash Cannon": "加农光炮",
    "Hydro Pump": "水炮",
    "Ice Beam": "冰冻光束",
    "Dragon Energy": "巨龙威能",
    "Dark Pulse": "恶之波动",
    "Flamethrower": "喷射火焰",
    "Heat Wave": "热风",
    "Eruption": "喷烟",
    "Yawn": "哈欠",
    "Stealth Rock": "撒菱",
    "Toxic Spikes": "毒菱",
    "Stomping Tantrum": "跺脚",
    "Scary Face": "鬼面",
    "Blizzard": "暴风雪",
    "Freeze-Dry": "冷冻干燥",
    "Aurora Veil": "极光幕"
}

# 性格中文名称映射
NATURE_NAME_ZH = {
    "Adamant": "固执",
    "Jolly": "爽朗",
    "Modest": "内敛",
    "Timid": "胆小",
    "Impish": "淘气",
    "Careful": "慎重",
    "Bold": "大胆",
    "Calm": "温和",
    "Brave": "勇敢",
    "Quiet": "冷静",
    "Relaxed": "悠闲",
    "Sassy": "自大"
}

def get_pokemon_set(pokemon_name: str) -> dict:
    """获取宝可梦的推荐配置"""
    return DEFAULT_SETS.get(pokemon_name, {
        "moves": ["根据环境选择", "根据环境选择", "根据环境选择", "守住"],
        "items": ["气势披带"],
        "natures": ["根据build选择"],
        "role": "待分析"
    })
