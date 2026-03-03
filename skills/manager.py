#!/usr/bin/env python3
"""
技能管理脚本 - 启用/禁用/查看技能
"""
import os
import sys
import json
import argparse
from pathlib import Path

# 技能目录
SKILLS_DIR = Path(__file__).parent / "skills"

def list_skills():
    """列出所有可用技能"""
    print("=" * 60)
    print("📦 可用技能列表")
    print("=" * 60)
    
    categories = {
        "core": "🎯 核心技能",
        "data": "📊 数据技能",
        "analysis": "📈 分析技能"
    }
    
    for cat_dir, cat_name in categories.items():
        cat_path = SKILLS_DIR / cat_dir
        if not cat_path.exists():
            continue
            
        print(f"\n{cat_name}")
        print("-" * 40)
        
        for skill_dir in cat_path.iterdir():
            if skill_dir.is_dir():
                skill_name = skill_dir.name
                init_file = skill_dir / "__init__.py"
                if init_file.exists():
                    # 读取技能描述
                    with open(init_file) as f:
                        first_line = f.readline()
                        desc = first_line.strip('#" \n') if first_line.startswith('#') else skill_name
                    print(f"  ✅ {skill_name:<20} - {desc}")
                else:
                    print(f"  ⚠️  {skill_name:<20} - 未初始化")

def enable_skill(skill_name: str):
    """启用技能"""
    print(f"🚀 启用技能: {skill_name}")
    
    # 查找技能
    skill_path = None
    for cat in ["core", "data", "analysis"]:
        path = SKILLS_DIR / cat / skill_name
        if path.exists():
            skill_path = path
            break
    
    if not skill_path:
        print(f"❌ 技能不存在: {skill_name}")
        return False
    
    # 添加到已启用列表
    enabled_file = SKILLS_DIR / "enabled.json"
    enabled = []
    if enabled_file.exists():
        with open(enabled_file) as f:
            enabled = json.load(f)
    
    if skill_name not in enabled:
        enabled.append(skill_name)
        with open(enabled_file, 'w') as f:
            json.dump(enabled, f, indent=2)
    
    print(f"✅ 技能已启用: {skill_name}")
    print(f"💡 重启服务以应用更改: ./production.sh restart")
    return True

def disable_skill(skill_name: str):
    """禁用技能"""
    print(f"🛑 禁用技能: {skill_name}")
    
    enabled_file = SKILLS_DIR / "enabled.json"
    if not enabled_file.exists():
        print("❌ 没有启用的技能")
        return False
    
    with open(enabled_file) as f:
        enabled = json.load(f)
    
    if skill_name in enabled:
        enabled.remove(skill_name)
        with open(enabled_file, 'w') as f:
            json.dump(enabled, f, indent=2)
        print(f"✅ 技能已禁用: {skill_name}")
    else:
        print(f"⚠️ 技能未启用: {skill_name}")
    
    return True

def skill_status():
    """查看技能状态"""
    print("=" * 60)
    print("📊 技能状态")
    print("=" * 60)
    
    enabled_file = SKILLS_DIR / "enabled.json"
    enabled = []
    if enabled_file.exists():
        with open(enabled_file) as f:
            enabled = json.load(f)
    
    print(f"\n✅ 已启用技能 ({len(enabled)}):")
    for skill in enabled:
        print(f"  • {skill}")
    
    if not enabled:
        print("  (无)")
    
    print("\n💡 使用 'python skills/manager.py list' 查看所有可用技能")

def main():
    parser = argparse.ArgumentParser(description="Crypto Daily Analyzer 技能管理")
    parser.add_argument("command", choices=["list", "enable", "disable", "status"],
                       help="管理命令")
    parser.add_argument("skill", nargs="?", help="技能名称")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_skills()
    elif args.command == "enable":
        if not args.skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        enable_skill(args.skill)
    elif args.command == "disable":
        if not args.skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        disable_skill(args.skill)
    elif args.command == "status":
        skill_status()

if __name__ == "__main__":
    main()
