#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话旅游规划 API 服务
基于 supervisor_agent.py 中的 run_multi_turn_chat 函数
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import sys
import os
from typing import Dict, Any, Generator
import logging
from datetime import datetime
import uuid

# 添加路径以导入相关模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from supervisor_agent import run_multi_turn_chat
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保 supervisor_agent.py 文件存在并且路径正确")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 存储会话状态（实际生产环境中应该使用数据库或缓存）
sessions = {}

def extract_latest_content(messages):
    """从消息列表中提取最新的有效内容"""
    if not messages:
        return ""
    
    # 从最后一条消息开始查找有效内容
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content:
            content = msg.content.strip()
            # 过滤掉系统转移消息
            if content and not content.startswith('Successfully transferred') and \
               not content.startswith('Transferring back') and \
               content != 'Successfully transferred back to supervisor':
                return content
    
    return ""

class MultiTurnChatSession:
    """多轮对话会话管理"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history = []
        self.user_inputs_only = []  # 只保存用户输入
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        
        # 只保存用户输入到专门的列表中
        if role == "user":
            self.user_inputs_only.append(message)
            # 只保留最近5轮用户输入
            if len(self.user_inputs_only) > 5:
                self.user_inputs_only = self.user_inputs_only[-5:]
        
        self.last_activity = datetime.now()
    
    def get_context(self) -> str:
        """获取对话上下文 - 包含完整的对话历史"""
        if not self.conversation_history:
            return ""
        
        # 使用完整的对话历史，但限制长度
        context_parts = []
        # 只取最近的10轮对话（20条消息）
        recent_messages = self.conversation_history[-20:] if len(self.conversation_history) > 20 else self.conversation_history
        
        for msg in recent_messages[:-1]:  # 排除当前输入
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)

def get_or_create_session(session_id: str) -> MultiTurnChatSession:
    """获取或创建会话"""
    if session_id not in sessions:
        sessions[session_id] = MultiTurnChatSession(session_id)
    return sessions[session_id]

@app.route('/api/multi-turn-chat', methods=['POST'])
def multi_turn_chat():
    """多轮对话 API 端点"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "请求体不能为空",
                "status": "error"
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({
                "error": "消息内容不能为空",
                "status": "error"
            }), 400
        
        # 获取会话
        session = get_or_create_session(session_id)
        
        # 构建包含上下文的请求
        context = session.get_context()
        if context:
            full_request = f"对话历史:\n{context}\n\n用户当前输入: {user_message}"
        else:
            full_request = user_message
        
        logger.info(f"处理会话 {session_id} 的请求: {user_message}")
        
        # 添加用户消息到历史
        session.add_message("user", user_message)
        
        # 调用多轮对话函数
        response_chunks = []
        full_response = ""
        
        try:
            for chunk in run_multi_turn_chat(full_request):
                response_chunks.append(chunk)
                # 提取响应内容
                if isinstance(chunk, dict):
                    for key, value in chunk.items():
                        if isinstance(value, dict) and 'messages' in value:
                            for msg in value['messages']:
                                if hasattr(msg, 'content') and msg.content:
                                    full_response = msg.content
        
        except Exception as e:
            logger.error(f"调用 run_multi_turn_chat 失败: {e}")
            return jsonify({
                "error": f"处理请求时发生错误: {str(e)}",
                "status": "error"
            }), 500
        
        # 清理响应内容
        full_response = full_response.strip()
        if not full_response:
            full_response = "抱歉，我没有生成有效的响应，请重新尝试。"
        
        # 添加系统响应到历史
        session.add_message("assistant", full_response)
        
        return jsonify({
            "response": full_response,
            "session_id": session_id,
            "status": "success",
            "conversation_length": len(session.conversation_history),
            "chunks": response_chunks  # 可选：返回原始chunks用于调试
        })
        
    except Exception as e:
        logger.error(f"API 处理失败: {e}")
        return jsonify({
            "error": f"服务器内部错误: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/multi-turn-chat/stream', methods=['POST'])
def multi_turn_chat_stream():
    """流式多轮对话 API 端点 - 实现真正的实时流式更新"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "请求体不能为空",
                "status": "error"
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({
                "error": "消息内容不能为空",
                "status": "error"
            }), 400
        
        # 获取会话
        session = get_or_create_session(session_id)
        
        # 构建包含上下文的请求
        context = session.get_context()
        if context:
            full_request = f"对话历史:\n{context}\n\n用户当前输入: {user_message}"
        else:
            full_request = user_message
        
        logger.info(f"处理流式会话 {session_id} 的请求: {user_message}")
        
        # 添加用户消息到历史
        session.add_message("user", user_message)
        
        def generate_stream():
            """生成实时流式响应 - 优化版"""
            full_response = ""
            agent_responses = {}  # 存储每个智能体的累积响应
            current_agent = None
            
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'session_id': session_id, 'timestamp': datetime.now().isoformat()})}\n\n"
                
                for chunk in run_multi_turn_chat(full_request):
                    if isinstance(chunk, dict):
                        print(chunk)
                        logger.debug(f"处理chunk: {chunk}")
                        
                        # 处理每个智能体的数据
                        for agent_key, agent_data in chunk.items():
                            if isinstance(agent_data, dict) and 'messages' in agent_data:
                                # 获取最新的有效消息内容
                                latest_content = extract_latest_content(agent_data['messages'])
                                
                                if latest_content and latest_content.strip():
                                    content = latest_content.strip()
                                    
                                    # 如果是新的智能体，发送开始信号
                                    if agent_key not in agent_responses:
                                        yield f"data: {json.dumps({'type': 'agent_start', 'agent': agent_key, 'timestamp': datetime.now().isoformat()})}\n\n"
                                        print(f"data: {json.dumps({'type': 'agent_start', 'agent': agent_key, 'timestamp': datetime.now().isoformat()})}\n\n")
                                        agent_responses[agent_key] = ''
                                        current_agent = agent_key
                                        
                                        # 小延迟确保前端处理
                                        import time
                                        time.sleep(0.03)
                                    
                                    # 检查内容是否有实质性更新
                                    previous_content = agent_responses.get(agent_key, '')
                                    if content != previous_content and len(content) > len(previous_content):
                                        # 更新智能体响应
                                        agent_responses[agent_key] = content
                                        current_agent = agent_key
                                        
                                        # 发送内容更新
                                        stream_data = {
                                            'type': 'content_update',
                                            'agent': agent_key,
                                            'content': content,
                                            'timestamp': datetime.now().isoformat(),
                                            'content_length': len(content),
                                            'is_incremental': len(content) > len(previous_content)
                                        }
                                        yield f"data: {json.dumps(stream_data)}\n\n"
                                        print(f"data: {json.dumps(stream_data)}\n\n")
                                        # 更新完整响应（使用最新的最长内容）
                                        if len(content) > len(full_response):
                                            full_response = content
                                        
                                        # 减少延迟
                                        import time
                                        time.sleep(0.01)
                
                # 发送最终完成信号
                if current_agent and full_response:
                    # 标记当前智能体完成
                    yield f"data: {json.dumps({'type': 'agent_complete', 'agent': current_agent, 'timestamp': datetime.now().isoformat()})}\n\n"
                    print(f"data: {json.dumps({'type': 'agent_complete', 'agent': current_agent, 'timestamp': datetime.now().isoformat()})}\n\n")
                
                # 发送整体完成信号
                completion_data = {
                    'type': 'done',
                    'full_response': full_response,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'agents_used': list(agent_responses.keys())
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                print(f"data: {json.dumps(completion_data)}\n\n")
                # 添加完整响应到历史
                if full_response.strip():
                    session.add_message("assistant", full_response.strip())
                
            except Exception as e:
                logger.error(f"流式处理失败: {e}")
                error_data = {
                    'type': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'X-Accel-Buffering': 'no'  # 禁用nginx缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"流式 API 处理失败: {e}")
        return jsonify({
            "error": f"服务器内部错误: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/multi-turn-chat/history/<session_id>', methods=['GET'])
def get_conversation_history(session_id: str):
    """获取对话历史"""
    try:
        if session_id not in sessions:
            return jsonify({
                "history": [],
                "session_id": session_id,
                "status": "success"
            })
        
        session = sessions[session_id]
        return jsonify({
            "history": session.conversation_history,
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({
            "error": f"获取对话历史失败: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/multi-turn-chat/reset/<session_id>', methods=['POST'])
def reset_conversation(session_id: str):
    """重置对话历史"""
    try:
        if session_id in sessions:
            del sessions[session_id]
        
        return jsonify({
            "message": f"会话 {session_id} 已重置",
            "session_id": session_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"重置会话失败: {e}")
        return jsonify({
            "error": f"重置会话失败: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/multi-turn-chat/sessions', methods=['GET'])
def list_sessions():
    """列出所有活跃会话"""
    try:
        session_list = []
        for session_id, session in sessions.items():
            session_list.append({
                "session_id": session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": len(session.conversation_history)
            })
        
        return jsonify({
            "sessions": session_list,
            "total_count": len(session_list),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"列出会话失败: {e}")
        return jsonify({
            "error": f"列出会话失败: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "multi-turn-chat-api",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    })

if __name__ == '__main__':
    print("🚀 启动多轮对话旅游规划 API 服务...")
    print("📍 API 端点:")
    print("  - POST /api/multi-turn-chat - 多轮对话")
    print("  - POST /api/multi-turn-chat/stream - 流式多轮对话")
    print("  - GET /api/multi-turn-chat/history/<session_id> - 获取对话历史")
    print("  - POST /api/multi-turn-chat/reset/<session_id> - 重置对话")
    print("  - GET /api/multi-turn-chat/sessions - 列出所有会话")
    print("  - GET /api/health - 健康检查")
    print("🌐 服务地址: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
