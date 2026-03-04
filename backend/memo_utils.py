#!/usr/bin/env python3
"""Memo extraction helpers for Star Office backend.

P1 step: extraction without behavior change.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import random
import re


def get_yesterday_date_str() -> str:
    """获取昨天的日期字符串 YYYY-MM-DD"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def sanitize_content(text: str) -> str:
    """清理内容，保护隐私"""
    # 移除 OpenID、User ID 等
    text = re.sub(r'ou_[a-f0-9]+', '[用户]', text)
    text = re.sub(r'user_id="[^"]+"', 'user_id="[隐藏]"', text)

    # 移除 IP 地址、路径等敏感信息
    text = re.sub(r'/root/[^"\s]+', '[路径]', text)
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', text)

    # 移除电话号码、邮箱等
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[邮箱]', text)
    text = re.sub(r'1[3-9]\d{9}', '[手机号]', text)

    return text


def extract_memo_from_file(file_path: str) -> str:
    """从 memory 文件中提取适合展示的 memo 内容（睿智风格的总结）"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取真实内容，不做过度包装
        lines = content.strip().split("\n")

        # 提取核心要点
        core_points = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("- "):
                core_points.append(line[2:].strip())
            elif len(line) > 10:
                core_points.append(line)

        if not core_points:
            return "「昨日无事记录」\n\n若有恒，何必三更眠五更起；最无益，莫过一日曝十日寒。"

        # 从核心内容中提取 2-3 个关键点
        selected_points = core_points[:3]

        # 睿智语录库
        wisdom_quotes = [
            "「工欲善其事，必先利其器。」",
            "「不积跬步，无以至千里；不积小流，无以成江海。」",
            "「知行合一，方可致远。」",
            "「业精于勤，荒于嬉；行成于思，毁于随。」",
            "「路漫漫其修远兮，吾将上下而求索。」",
            "「昨夜西风凋碧树，独上高楼，望尽天涯路。」",
            "「衣带渐宽终不悔，为伊消得人憔悴。」",
            "「众里寻他千百度，蓦然回首，那人却在，灯火阑珊处。」",
            "「世事洞明皆学问，人情练达即文章。」",
            "「纸上得来终觉浅，绝知此事要躬行。」"
        ]

        quote = random.choice(wisdom_quotes)

        # 组合内容
        result = []

        # 添加核心内容
        if selected_points:
            for point in selected_points:
                # 隐私清理
                point = sanitize_content(point)
                # 截断过长的内容
                if len(point) > 40:
                    point = point[:37] + "..."
                # 每行最多 20 字
                if len(point) <= 20:
                    result.append(f"· {point}")
                else:
                    # 按 20 字切分
                    for j in range(0, len(point), 20):
                        chunk = point[j:j+20]
                        if j == 0:
                            result.append(f"· {chunk}")
                        else:
                            result.append(f"  {chunk}")

        # 添加睿智语录
        if quote:
            if len(quote) <= 20:
                result.append(f"\n{quote}")
            else:
                for j in range(0, len(quote), 20):
                    chunk = quote[j:j+20]
                    if j == 0:
                        result.append(f"\n{chunk}")
                    else:
                        result.append(chunk)

        return "\n".join(result).strip()

    except Exception as e:
        print(f"提取 memo 失败: {e}")
        return "「昨日记录加载失败」\n\n「往者不可谏，来者犹可追。」"
