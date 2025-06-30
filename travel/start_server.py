#!/usr/bin/env python3
"""
启动脚本 - 用于启动旅游规划API服务器
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
        import fastapi
        import uvicorn
        import requests
        import langchain_core
        import langchain_openai
        import langgraph
        import dotenv
        import json_repair
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    print("🔍 检查环境变量...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ 未找到 .env 文件")
        print("请创建 .env 文件并配置以下变量:")
        print("REACT_API_KEY=your_api_key")
        print("AMAP_API_KEY=your_amap_key")
        return False
    
    # 检查必要的环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["REACT_API_KEY", "AMAP_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    print("✅ 环境变量配置正确")
    return True

def check_imports():
    """检查关键模块导入"""
    print("🔍 检查模块导入...")
    
    try:
        # 检查 supervisor_agent 模块
        from supervisor_agent import (
            need_collect_agent,
            create_travel_supervisor,
            create_travel_supervisor_flexible
        )
        print("✅ supervisor_agent 模块导入成功")
        
        # 检查 workflow_client 模块
        try:
            from workflow_client import WorkflowClient
            print("✅ workflow_client 模块导入成功")
        except ImportError:
            print("⚠️ workflow_client 模块导入失败，部分功能可能不可用")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def start_server(host="0.0.0.0", port=8000, reload=True):
    """启动服务器"""
    print(f"🚀 启动服务器 http://{host}:{port}")
    
    try:
        # 使用 uvicorn 启动服务器
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api_server:app",
            "--host", host,
            "--port", str(port),
            "--log-level", "info"
        ]
        
        if reload:
            cmd.append("--reload")
        
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    print("🧳 智能旅游规划 API 服务器启动器")
    print("=" * 50)
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 工作目录: {script_dir}")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境变量
    if not check_env_file():
        sys.exit(1)
    
    # 检查模块导入
    if not check_imports():
        sys.exit(1)
    
    print("\n✅ 所有检查通过，准备启动服务器...")
    print("💡 提示: 按 Ctrl+C 停止服务器")
    print("🌐 API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
