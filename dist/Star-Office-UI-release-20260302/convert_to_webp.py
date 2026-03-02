#!/usr/bin/env python3
"""
批量转换 PNG 资源为 WebP 格式
- 精灵图使用无损转换
- 背景图等使用有损转换（质量 85）
"""

import os
from PIL import Image

# 路径
FRONTEND_DIR = "/root/.openclaw/workspace/star-office-ui/frontend"
STATIC_DIR = os.path.join(FRONTEND_DIR, "")

# 文件分类配置
# 无损转换：精灵图、需要保持透明精度的
LOSSLESS_FILES = [
    "star-idle-spritesheet.png",
    "star-researching-spritesheet.png",
    "star-working-spritesheet.png",
    "sofa-busy-spritesheet.png",
    "plants-spritesheet.png",
    "posters-spritesheet.png",
    "coffee-machine-spritesheet.png",
    "serverroom-spritesheet.png"
]

# 有损转换：背景图等，质量 85
LOSSY_FILES = [
    "office_bg.png",
    "sofa-idle.png",
    "desk.png"
]


def convert_to_webp(input_path, output_path, lossless=True, quality=85):
    """转换单个文件为 WebP"""
    try:
        img = Image.open(input_path)
        
        # 保存为 WebP
        if lossless:
            img.save(output_path, 'WebP', lossless=True, method=6)
        else:
            img.save(output_path, 'WebP', quality=quality, method=6)
        
        # 计算文件大小
        orig_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        savings = (1 - new_size / orig_size) * 100
        
        print(f"✅ {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        print(f"   原大小: {orig_size/1024:.1f}KB -> 新大小: {new_size/1024:.1f}KB (-{savings:.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ {os.path.basename(input_path)} 转换失败: {e}")
        return False


def main():
    print("=" * 60)
    print("PNG → WebP 批量转换工具")
    print("=" * 60)
    
    # 检查目录
    if not os.path.exists(STATIC_DIR):
        print(f"❌ 目录不存在: {STATIC_DIR}")
        return
    
    success_count = 0
    fail_count = 0
    
    print("\n📁 开始转换...\n")
    
    # 转换无损文件
    print("--- 无损转换（精灵图）---")
    for filename in LOSSLESS_FILES:
        input_path = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(input_path):
            print(f"⚠️  文件不存在，跳过: {filename}")
            continue
        
        output_path = os.path.join(STATIC_DIR, filename.replace(".png", ".webp"))
        if convert_to_webp(input_path, output_path, lossless=True):
            success_count += 1
        else:
            fail_count += 1
    
    # 转换有损文件
    print("\n--- 有损转换（背景图，质量 85）---")
    for filename in LOSSY_FILES:
        input_path = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(input_path):
            print(f"⚠️  文件不存在，跳过: {filename}")
            continue
        
        output_path = os.path.join(STATIC_DIR, filename.replace(".png", ".webp"))
        if convert_to_webp(input_path, output_path, lossless=False, quality=85):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"转换完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)
    print("\n📝 注意:")
    print("  - PNG 原文件已保留，不会删除")
    print("  - 需要修改前端代码引用 .webp 文件")
    print("  - 如需回滚，只需把代码改回引用 .png 即可")


if __name__ == "__main__":
    main()

