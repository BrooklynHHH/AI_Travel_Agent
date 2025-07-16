#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化多轮对话系统启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    try:
        import flask
        import flask_cors
        print("✅ Flask依赖已安装")
    except ImportError:
        print("❌ Flask依赖未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    
    # 检查requirements.txt中的其他依赖
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        print("📦 安装requirements.txt中的依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    
    print("✅ 依赖检查完成")

def check_environment():
    """检查环境配置"""
    print("🔧 检查环境配置...")
    
    # 检查travel目录（上级目录）
    agent_mi_path = Path(__file__).parent.parent
    if not agent_mi_path.exists():
        print(f"❌ 找不到travel目录: {agent_mi_path}")
        print("请确保travel目录存在")
        return False
    
    # 检查关键文件
    required_files = [
        "supervisor_agent.py",
        "enhanced_stream_api_V1.py"
    ]
    
    for file_name in required_files:
        file_path = agent_mi_path / file_name
        if not file_path.exists():
            print(f"❌ 找不到必需文件: {file_path}")
            return False
    
    print("✅ 环境配置检查完成")
    return True

def start_server():
    """启动服务器"""
    print("🚀 启动简化多轮对话API服务器...")
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(Path(__file__).parent)
    
    # 启动服务器
    server_script = Path(__file__).parent / "simple_multi_turn_api.py"
    
    try:
        subprocess.run([sys.executable, str(server_script)], check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 简化多轮对话系统启动器")
    print("=" * 60)
    
    # 1. 检查依赖
    try:
        check_dependencies()
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return
    
    # 2. 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请检查配置")
        return
    
    # 3. 启动服务器
    print("\n" + "=" * 60)
    print("🚀 准备启动服务器...")
    print("📍 服务地址: http://localhost:5000")
    print("📋 主要接口: POST /api/stream")
    print("🔧 测试命令: python test_simple_api.py")
    print("=" * 60)
    
    # 等待用户确认
    try:
        input("按回车键启动服务器，或Ctrl+C取消...")
    except KeyboardInterrupt:
        print("\n🛑 启动已取消")
        return
    
    start_server()

if __name__ == "__main__":
    main()
