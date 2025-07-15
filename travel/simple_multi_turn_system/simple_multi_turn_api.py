#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化多轮对话API服务器
严格按照用户需求实现 /api/stream 接口
"""

import sys
import os
import json
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# 添加路径以导入相关模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, '../agent-mi/travel'))

# 导入本地模块
from config import API_HOST, API_PORT, DEBUG_MODE, SUPERVISOR_CONFIG
from multi_turn_session import session_manager
from utils.logger import setup_logger, log_user_input, log_system_response, log_error, log_session_event
from utils.stream_handler import StreamHandler, create_error_stream, create_start_stream
from content_formatter import format_for_console

# 导入智能体模块
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from supervisor_agent import create_multi_turn_chat_supervisor
    from enhanced_stream_api_V1 import run_enhanced_streaming_api
except ImportError as e:
    print(f"导入智能体模块失败: {e}")
    print("请确保 agent-mi/travel 目录存在并且包含必要的模块")
    sys.exit(1)

# 设置日志
logger = setup_logger("simple_multi_turn_api")

# 创建Flask应用
app = Flask(__name__)
# 配置CORS，明确支持OPTIONS方法和所需的头部
CORS(app, 
     origins=['*'],  # 允许所有来源
     methods=['GET', 'POST', 'OPTIONS'],  # 明确允许OPTIONS方法
     allow_headers=['Content-Type', 'Authorization'],  # 允许的头部
     supports_credentials=False)

# 全局变量：supervisor实例
supervisor = None

def init_supervisor():
    """初始化supervisor"""
    global supervisor
    try:
        if supervisor is None:
            logger.info("正在初始化supervisor...")
            supervisor = create_multi_turn_chat_supervisor()
            logger.info("Supervisor初始化成功")
        return supervisor
    except Exception as e:
        logger.error(f"初始化supervisor失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查supervisor是否可用
        if supervisor is None:
            init_supervisor()
        
        # 清理过期会话
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Simple Multi-Turn Chat API",
            "supervisor_status": "ready" if supervisor else "not_ready",
            "active_sessions": session_manager.get_active_session_count(),
            "cleaned_sessions": cleaned_count,
            "version": "1.0.0"
        })
    except Exception as e:
        log_error(logger, e, "健康检查")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/stream', methods=['POST'])
def stream_endpoint():
    """
    核心流式接口
    接受用户输入，基于user_input_history实现多轮对话
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
        
        user_input = data.get('user_input', '').strip()
        if not user_input:
            return jsonify({"error": "user_input不能为空"}), 400
        
        # 获取或创建会话
        session_id = data.get('session_id')
        session = session_manager.get_or_create_session(session_id)
        
        # 记录用户输入
        log_user_input(logger, user_input, session.session_id)
        log_session_event(logger, "用户输入", session.session_id, f"输入长度: {len(user_input)}")
        
        # 添加用户输入到会话历史
        session.add_user_input(user_input)
        
        # 构建包含历史的请求
        user_input_history = session.get_user_input_history()
        
        # 构建上下文
        if len(user_input_history) > 1:
            # 多轮对话，包含历史
            context_parts = []
            context_parts.append("用户输入历史:")
            for i, hist_input in enumerate(user_input_history, 1):
                context_parts.append(f"{i}. {hist_input}")
            context_parts.append(f"\n当前用户输入: {user_input}")
            full_request = "\n".join(context_parts)
        else:
            # 首轮对话
            full_request = user_input
        
        logger.info(f"会话 {session.session_id}: 构建请求上下文，历史轮数: {len(user_input_history)}")
        
        # 确保supervisor已初始化
        if supervisor is None:
            init_supervisor()
        
        def generate_stream():
            """生成流式响应"""
            stream_handler = StreamHandler()
            final_response = ""
            
            try:
                # 发送开始信号
                start_data = {
                    "type": "start",
                    "message": "开始处理请求",
                    "session_id": session.session_id,
                    "user_input_history": user_input_history,
                    "timestamp": datetime.now().isoformat()
                }
                yield stream_handler.format_sse_data(start_data)
                
                
                # 调用智能体系统进行流式处理
                chunk_count = 0
                for chunk in run_enhanced_streaming_api(
                    user_input=full_request,
                    supervisor=supervisor,
                    **SUPERVISOR_CONFIG
                ):
                    chunk_count += 1
                    logger.debug(f"会话 {session.session_id}: 处理第 {chunk_count} 个数据块")
                    
                    # 使用流式处理器处理数据块
                    for formatted_chunk in stream_handler.process_stream_chunk(chunk, session.session_id):
                        yield formatted_chunk
                        
                        # 在控制台显示格式化内容（用于调试）
                        try:
                            chunk_data = json.loads(formatted_chunk.replace("data: ", "").strip())
                            if chunk_data.get("type") == "content_update":
                                console_output = format_for_console(chunk_data)
                                print(console_output, flush=True)
                        except:
                            pass  # 忽略格式化错误
                
                # 完成流式处理
                final_stream = stream_handler.finalize_stream(session.session_id)
                yield final_stream
                
                # 提取最终响应
                if stream_handler.content_buffer:
                    final_response = max(stream_handler.content_buffer.values(), key=len)
                
                # 添加系统响应到会话历史
                if final_response:
                    session.add_system_response(final_response, "supervisor")
                    log_system_response(logger, final_response, session.session_id)
                
                log_session_event(logger, "处理完成", session.session_id, f"响应长度: {len(final_response)}")
                
            except Exception as e:
                log_error(logger, e, "流式处理", session.session_id)
                error_stream = create_error_stream(f"处理请求时发生错误: {str(e)}", session.session_id)
                yield error_stream
        
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
        log_error(logger, e, "API接口")
        return jsonify({
            "error": str(e),
            "message": "API接口处理失败",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """列出所有会话"""
    try:
        sessions = session_manager.get_all_sessions_summary()
        return jsonify({
            "status": "success",
            "sessions": sessions,
            "total_count": len(sessions),
            "active_count": session_manager.get_active_session_count(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e, "列出会话")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取指定会话信息"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "会话不存在"}), 404
        
        return jsonify({
            "status": "success",
            "session": session.get_session_summary(),
            "user_input_history": session.get_user_input_history(),
            "conversation_context": session.get_conversation_context(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e, "获取会话")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除指定会话"""
    try:
        success = session_manager.remove_session(session_id)
        if success:
            log_session_event(logger, "会话删除", session_id)
            return jsonify({
                "status": "success",
                "message": f"会话 {session_id} 已删除",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "会话不存在"}), 404
    except Exception as e:
        log_error(logger, e, "删除会话")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<session_id>/clear', methods=['POST'])
def clear_session_history(session_id):
    """清空指定会话的历史记录"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "会话不存在"}), 404
        
        session.clear_history()
        log_session_event(logger, "历史清空", session_id)
        
        return jsonify({
            "status": "success",
            "message": f"会话 {session_id} 的历史记录已清空",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e, "清空会话历史")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status_endpoint():
    """服务状态接口"""
    try:
        return jsonify({
            "service": "Simple Multi-Turn Chat API",
            "version": "1.0.0",
            "status": "running",
            "supervisor_initialized": supervisor is not None,
            "active_sessions": session_manager.get_active_session_count(),
            "endpoints": [
                {"path": "/api/health", "method": "GET", "description": "健康检查"},
                {"path": "/api/stream", "method": "POST", "description": "流式多轮对话"},
                {"path": "/api/sessions", "method": "GET", "description": "列出所有会话"},
                {"path": "/api/sessions/<id>", "method": "GET", "description": "获取会话信息"},
                {"path": "/api/sessions/<id>", "method": "DELETE", "description": "删除会话"},
                {"path": "/api/sessions/<id>/clear", "method": "POST", "description": "清空会话历史"},
                {"path": "/api/status", "method": "GET", "description": "服务状态"}
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        log_error(logger, e, "状态接口")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "error": "接口不存在",
        "message": "请检查请求路径是否正确",
        "available_endpoints": ["/api/health", "/api/stream", "/api/sessions", "/api/status"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(error)}")
    return jsonify({
        "error": "内部服务器错误",
        "message": "服务器处理请求时发生错误",
        "timestamp": datetime.now().isoformat()
    }), 500

def startup():
    """应用启动时的初始化"""
    logger.info("Simple Multi-Turn Chat API 服务器启动中...")
    
    # 初始化supervisor
    try:
        init_supervisor()
        logger.info("✅ Supervisor初始化成功")
    except Exception as e:
        logger.error(f"❌ Supervisor初始化失败: {e}")
        raise
    
    logger.info("🚀 服务器启动完成")
    logger.info(f"📍 服务地址: http://{API_HOST}:{API_PORT}")
    logger.info("📋 主要接口:")
    logger.info("  - POST /api/stream - 流式多轮对话")
    logger.info("  - GET /api/health - 健康检查")
    logger.info("  - GET /api/sessions - 会话管理")

if __name__ == '__main__':
    # 在应用启动时初始化
    with app.app_context():
        startup()
    
    # 启动服务器
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=DEBUG_MODE,
        threaded=True
    )
