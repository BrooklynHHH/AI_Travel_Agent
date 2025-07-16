#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式处理工具模块
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Generator, Optional
from .logger import setup_logger

logger = setup_logger(__name__)

class StreamHandler:
    """流式数据处理器"""
    
    def __init__(self):
        self.current_agent = None
        self.content_buffer = {}
        
    def format_sse_data(self, data: Dict[str, Any]) -> str:
        """
        格式化为SSE数据格式
        
        Args:
            data: 要发送的数据
            
        Returns:
            格式化后的SSE数据字符串
        """
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            return f"data: {json_data}\n\n"
        except Exception as e:
            logger.error(f"格式化SSE数据失败: {e}")
            error_data = {
                "type": "error",
                "message": "数据格式化失败",
                "timestamp": datetime.now().isoformat()
            }
            return f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    def extract_content_from_messages(self, messages) -> str:
        """
        从消息列表中提取内容
        
        Args:
            messages: 消息列表
            
        Returns:
            提取的内容字符串
        """
        if not messages:
            return ""
        
        content_parts = []
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                content = msg.content.strip()
                # 过滤掉系统转移消息
                if (content and 
                    not content.startswith('Successfully transferred') and 
                    not content.startswith('Transferring back') and 
                    content != 'Successfully transferred back to supervisor'):
                    content_parts.append(content)
        
        return "\n".join(content_parts)
    
    def detect_content_type(self, content: str) -> str:
        """
        检测内容类型
        
        Args:
            content: 内容字符串
            
        Returns:
            内容类型
        """
        if not content:
            return "text"
        
        content_lower = content.lower()
        
        # 检测推荐内容
        if any(keyword in content_lower for keyword in ['推荐', '景点', '风景', '旅游', '游览']):
            return "recommendation"
        
        # 检测错误信息
        if any(keyword in content_lower for keyword in ['错误', 'error', '失败', 'failed']):
            return "error"
        
        # 检测规划内容
        if any(keyword in content_lower for keyword in ['行程', '计划', '安排', '规划']):
            return "planning"
        
        # 检测交通信息
        if any(keyword in content_lower for keyword in ['交通', '车票', '飞机', '火车', '汽车']):
            return "transport"
        
        # 检测住宿信息
        if any(keyword in content_lower for keyword in ['酒店', '住宿', '宾馆', '民宿']):
            return "hotel"
        
        return "text"
    
    def process_stream_chunk(self, chunk: Dict[str, Any], session_id: str = None) -> Generator[str, None, None]:
        """
        处理流式数据块
        
        Args:
            chunk: 数据块
            session_id: 会话ID
            
        Yields:
            格式化的SSE数据
        """
        try:
            # 检查是否包含智能体数据
            for agent_key, agent_data in chunk.items():
                if isinstance(agent_data, dict) and 'messages' in agent_data:
                    # 提取内容
                    content = self.extract_content_from_messages(agent_data['messages'])
                    
                    if content and content.strip():
                        # 检查是否是新的智能体
                        if agent_key != self.current_agent:
                            # 发送智能体开始信号
                            start_data = {
                                "type": "agent_start",
                                "agent": agent_key,
                                "agent_name": self.get_agent_display_name(agent_key),
                                "timestamp": datetime.now().isoformat(),
                                "session_id": session_id
                            }
                            yield self.format_sse_data(start_data)
                            self.current_agent = agent_key
                            time.sleep(0.05)  # 小延迟确保前端处理
                        
                        # 检查内容是否有更新
                        previous_content = self.content_buffer.get(agent_key, "")
                        if len(content) > len(previous_content):
                            # 更新缓冲区
                            self.content_buffer[agent_key] = content
                            
                            # 发送内容更新
                            content_type = self.detect_content_type(content)
                            update_data = {
                                "type": "content_update",
                                "agent": agent_key,
                                "agent_name": self.get_agent_display_name(agent_key),
                                "content": content,
                                "content_type": content_type,
                                "content_length": len(content),
                                "is_incremental": len(content) > len(previous_content),
                                "timestamp": datetime.now().isoformat(),
                                "session_id": session_id
                            }
                            yield self.format_sse_data(update_data)
                            
                            # 记录日志
                            logger.debug(f"流式更新 - {agent_key}: {len(content)}字符")
            
            # 发送原始数据（用于调试）
            raw_data = {
                "type": "raw_chunk",
                "data": chunk,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
            yield self.format_sse_data(raw_data)
            
        except Exception as e:
            logger.error(f"处理流式数据块失败: {e}")
            error_data = {
                "type": "error",
                "message": f"处理数据失败: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
            yield self.format_sse_data(error_data)
    
    def finalize_stream(self, session_id: str = None) -> str:
        """
        完成流式处理
        
        Args:
            session_id: 会话ID
            
        Returns:
            完成信号的SSE数据
        """
        # 获取最终响应（使用最长的内容）
        final_response = ""
        if self.content_buffer:
            final_response = max(self.content_buffer.values(), key=len)
        
        # 发送完成信号
        done_data = {
            "type": "done",
            "message": "处理完成",
            "final_response": final_response,
            "agents_used": list(self.content_buffer.keys()),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        # 清理缓冲区
        self.reset()
        
        return self.format_sse_data(done_data)
    
    def get_agent_display_name(self, agent_key: str) -> str:
        """获取智能体显示名称"""
        agent_names = {
            'supervisor': '总控智能体',
            'tour_search_agent': '景点搜索专家',
            'day_plan_agent': '行程规划师',
            'live_transport_agent': '交通住宿顾问',
            'travel_butler_agent': '旅行管家'
        }
        return agent_names.get(agent_key, agent_key)
    
    def reset(self):
        """重置处理器状态"""
        self.current_agent = None
        self.content_buffer = {}
        logger.debug("流式处理器已重置")

def create_error_stream(error_message: str, session_id: str = None) -> str:
    """
    创建错误流式响应
    
    Args:
        error_message: 错误消息
        session_id: 会话ID
        
    Returns:
        错误的SSE数据
    """
    handler = StreamHandler()
    error_data = {
        "type": "error",
        "message": error_message,
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id
    }
    return handler.format_sse_data(error_data)

def create_start_stream(session_id: str = None) -> str:
    """
    创建开始流式响应
    
    Args:
        session_id: 会话ID
        
    Returns:
        开始的SSE数据
    """
    handler = StreamHandler()
    start_data = {
        "type": "start",
        "message": "开始处理请求",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id
    }
    return handler.format_sse_data(start_data)
