#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化多轮对话API测试脚本
"""

import requests
import json
import time
import uuid
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:5000"
TEST_SESSION_ID = str(uuid.uuid4())

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_stream_api(user_input, session_id=None):
    """测试流式API接口"""
    print(f"\n💬 测试流式API - 用户输入: {user_input}")
    
    # 构建请求数据
    data = {"user_input": user_input}
    if session_id:
        data["session_id"] = session_id
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/stream",
            json=data,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("📡 流式响应:")
            print("-" * 50)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data_str = line_str[6:]  # 移除 'data: ' 前缀
                            data_obj = json.loads(data_str)
                            
                            # 格式化显示
                            msg_type = data_obj.get('type', 'unknown')
                            timestamp = data_obj.get('timestamp', '')
                            
                            if msg_type == 'start':
                                print(f"🚀 [{timestamp}] 开始处理: {data_obj.get('message', '')}")
                            elif msg_type == 'agent_start':
                                agent_name = data_obj.get('agent_name', '')
                                print(f"🤖 [{timestamp}] {agent_name} 开始工作")
                            elif msg_type == 'content_update':
                                agent_name = data_obj.get('agent_name', '')
                                content = data_obj.get('content', '')
                                print(f"📝 [{timestamp}] {agent_name}: {content[:100]}...")
                            elif msg_type == 'done':
                                print(f"✅ [{timestamp}] 处理完成")
                                final_response = data_obj.get('final_response', '')
                                if final_response:
                                    print(f"📋 最终响应: {final_response[:200]}...")
                            elif msg_type == 'error':
                                print(f"❌ [{timestamp}] 错误: {data_obj.get('message', '')}")
                            else:
                                print(f"📄 [{timestamp}] {msg_type}: {str(data_obj)[:100]}...")
                                
                        except json.JSONDecodeError:
                            print(f"⚠️  无法解析JSON: {line_str}")
            
            print("-" * 50)
            return True
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 流式API测试失败: {e}")
        return False

def test_session_management():
    """测试会话管理接口"""
    print("\n📋 测试会话管理接口...")
    
    try:
        # 列出所有会话
        response = requests.get(f"{API_BASE_URL}/api/sessions")
        print(f"列出会话 - 状态码: {response.status_code}")
        if response.status_code == 200:
            sessions_data = response.json()
            print(f"活跃会话数: {sessions_data.get('active_count', 0)}")
            print(f"总会话数: {sessions_data.get('total_count', 0)}")
        
        # 获取特定会话信息
        if TEST_SESSION_ID:
            response = requests.get(f"{API_BASE_URL}/api/sessions/{TEST_SESSION_ID}")
            print(f"获取会话信息 - 状态码: {response.status_code}")
            if response.status_code == 200:
                session_data = response.json()
                session_info = session_data.get('session', {})
                print(f"会话ID: {session_info.get('session_id', '')}")
                print(f"用户输入次数: {session_info.get('user_input_count', 0)}")
                print(f"总消息数: {session_info.get('total_message_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 会话管理测试失败: {e}")
        return False

def test_status_endpoint():
    """测试状态接口"""
    print("\n📊 测试状态接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/status")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"服务: {status_data.get('service', '')}")
            print(f"版本: {status_data.get('version', '')}")
            print(f"状态: {status_data.get('status', '')}")
            print(f"Supervisor初始化: {status_data.get('supervisor_initialized', False)}")
            print("可用接口:")
            for endpoint in status_data.get('endpoints', []):
                print(f"  - {endpoint.get('method', '')} {endpoint.get('path', '')} - {endpoint.get('description', '')}")
        return True
    except Exception as e:
        print(f"❌ 状态接口测试失败: {e}")
        return False

def run_multi_turn_conversation():
    """运行多轮对话测试"""
    print("\n🔄 开始多轮对话测试...")
    
    # 测试对话序列
    conversation_steps = [
        "推荐风景",
        "我想去北京旅游",
        "帮我规划3天的行程",
        "推荐一些当地美食"
    ]
    
    session_id = str(uuid.uuid4())
    print(f"使用会话ID: {session_id}")
    
    for i, user_input in enumerate(conversation_steps, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        success = test_stream_api(user_input, session_id)
        if not success:
            print(f"❌ 第 {i} 轮对话失败")
            break
        
        # 短暂等待
        time.sleep(2)
    
    return session_id

def main():
    """主测试函数"""
    print("🚀 开始简化多轮对话API测试")
    print(f"📍 API地址: {API_BASE_URL}")
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 健康检查
    if not test_health_check():
        print("❌ 健康检查失败，停止测试")
        return
    
    # 2. 状态检查
    if not test_status_endpoint():
        print("❌ 状态检查失败")
    
    # 3. 单次流式API测试
    print("\n🧪 单次流式API测试")
    test_stream_api("推荐风景")
    
    # 4. 多轮对话测试
    test_session_id = run_multi_turn_conversation()
    
    # 5. 会话管理测试
    if test_session_id:
        global TEST_SESSION_ID
        TEST_SESSION_ID = test_session_id
        test_session_management()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")

if __name__ == "__main__":
    main()
