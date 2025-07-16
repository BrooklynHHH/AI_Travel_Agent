#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容格式化模块
基于接口数据字段类型进行差异化展示
"""

from typing import Dict, Any
from datetime import datetime
from utils.logger import setup_logger
from config import CONTENT_TYPES

logger = setup_logger(__name__)

class ContentFormatter:
    """内容格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.content_type_icons = CONTENT_TYPES
    
    def format_stream_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据流式数据的字段类型进行格式化
        
        Args:
            data: 流式数据字典
            
        Returns:
            格式化后的数据
        """
        # 获取数据类型
        data_type = data.get("type", "text")
        content = data.get("content", "")
        agent = data.get("agent", "system")
        
        # 根据数据类型进行格式化
        if data_type == "start":
            return self._format_start_message(data)
        elif data_type == "agent_start":
            return self._format_agent_start(data)
        elif data_type == "content_update":
            return self._format_content_update(data)
        elif data_type == "done":
            return self._format_completion(data)
        elif data_type == "error":
            return self._format_error_message(data)
        else:
            return self._format_generic_message(data)
    
    def _format_start_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化开始消息"""
        return {
            "type": "start",
            "icon": "🚀",
            "title": "开始处理",
            "content": data.get("message", "开始处理请求"),
            "display_style": "system",
            "color": "#2196F3",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_agent_start(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化智能体开始消息"""
        agent = data.get("agent", "unknown")
        agent_name = data.get("agent_name", agent)
        
        # 根据智能体类型选择图标
        agent_icons = {
            "supervisor": "🎯",
            "tour_search_agent": "🔍",
            "day_plan_agent": "📅",
            "live_transport_agent": "🚗",
            "travel_butler_agent": "🎒"
        }
        
        icon = agent_icons.get(agent, "🤖")
        
        return {
            "type": "agent_start",
            "icon": icon,
            "title": f"{agent_name} 开始工作",
            "content": f"{agent_name} 正在处理您的请求...",
            "agent": agent,
            "agent_name": agent_name,
            "display_style": "agent_notification",
            "color": "#4CAF50",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_content_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化内容更新消息"""
        agent = data.get("agent", "system")
        agent_name = data.get("agent_name", agent)
        content = data.get("content", "")
        content_type = data.get("content_type", "text")
        
        # 根据智能体类型选择图标和颜色
        agent_config = {
            "supervisor": {"icon": "🎯", "color": "#673AB7"},
            "tour_search_agent": {"icon": "🔍", "color": "#2196F3"},
            "day_plan_agent": {"icon": "📅", "color": "#4CAF50"},
            "live_transport_agent": {"icon": "🚗", "color": "#FF9800"},
            "travel_butler_agent": {"icon": "🎒", "color": "#9C27B0"}
        }
        
        config = agent_config.get(agent, {"icon": "🤖", "color": "#607D8B"})
        
        return {
            "type": "content_update",
            "icon": config["icon"],
            "title": f"{agent_name} 回复",
            "content": content,
            "agent": agent,
            "agent_name": agent_name,
            "content_type": content_type,
            "content_length": data.get("content_length", len(content)),
            "is_incremental": data.get("is_incremental", False),
            "display_style": "content",
            "color": config["color"],
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_completion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化完成消息"""
        final_response = data.get("final_response", "")
        agents_used = data.get("agents_used", [])
        
        return {
            "type": "completion",
            "icon": "✅",
            "title": "处理完成",
            "content": data.get("message", "处理完成"),
            "final_response": final_response,
            "agents_used": agents_used,
            "display_style": "completion",
            "color": "#4CAF50",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_error_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化错误消息"""
        return {
            "type": "error",
            "icon": "❌",
            "title": "错误",
            "content": data.get("message", "发生错误"),
            "display_style": "error",
            "color": "#F44336",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_generic_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化通用消息"""
        return {
            "type": data.get("type", "text"),
            "icon": "📝",
            "title": "消息",
            "content": data.get("content", ""),
            "display_style": "normal",
            "color": "#333333",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
    
    def format_for_console(self, formatted_data: Dict[str, Any]) -> str:
        """
        为控制台输出格式化内容
        
        Args:
            formatted_data: 格式化后的数据
            
        Returns:
            适合控制台显示的字符串
        """
        icon = formatted_data.get("icon", "")
        title = formatted_data.get("title", "")
        content = formatted_data.get("content", "")
        timestamp = formatted_data.get("timestamp", "")
        
        # 解析时间戳
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = ""
        
        # 构建输出
        if formatted_data.get("type") == "content_update":
            # 内容更新使用简洁格式
            agent_name = formatted_data.get("agent_name", "")
            return f"[{time_str}] {icon} {agent_name}: {content}"
        elif formatted_data.get("type") in ["start", "agent_start", "completion"]:
            # 系统消息使用突出格式
            return f"\n{'='*50}\n{icon} {title}\n{content}\n{'='*50}\n"
        elif formatted_data.get("type") == "error":
            # 错误消息使用警告格式
            return f"\n{'!'*50}\n{icon} {title}: {content}\n{'!'*50}\n"
        else:
            # 普通消息
            return f"[{time_str}] {icon} {title}: {content}"
    
    def format_for_web(self, formatted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为Web前端格式化内容
        
        Args:
            formatted_data: 格式化后的数据
            
        Returns:
            适合Web显示的字典
        """
        # 直接返回格式化数据，添加Web特定字段
        web_data = formatted_data.copy()
        
        # 添加CSS类名
        web_data["css_class"] = f"message-{formatted_data.get('type', 'text')}"
        
        # 添加显示配置
        web_data["display_config"] = {
            "animation": self._get_animation_type(formatted_data.get("type")),
            "priority": self._get_display_priority(formatted_data.get("type")),
            "auto_scroll": formatted_data.get("type") == "content_update"
        }
        
        return web_data
    
    def _get_animation_type(self, message_type: str) -> str:
        """获取动画类型"""
        animation_map = {
            "start": "slideDown",
            "agent_start": "fadeInLeft",
            "content_update": "fadeIn",
            "completion": "bounceIn",
            "error": "shake"
        }
        return animation_map.get(message_type, "fadeIn")
    
    def _get_display_priority(self, message_type: str) -> int:
        """获取显示优先级"""
        priority_map = {
            "error": 1,
            "start": 2,
            "completion": 3,
            "agent_start": 4,
            "content_update": 5
        }
        return priority_map.get(message_type, 6)

# 全局格式化器实例
content_formatter = ContentFormatter()

def format_stream_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    便捷的流式数据格式化函数
    
    Args:
        data: 流式数据
        
    Returns:
        格式化后的数据
    """
    return content_formatter.format_stream_data(data)

def format_for_console(data: Dict[str, Any]) -> str:
    """
    便捷的控制台格式化函数
    
    Args:
        data: 数据字典
        
    Returns:
        控制台格式化字符串
    """
    formatted = content_formatter.format_stream_data(data)
    return content_formatter.format_for_console(formatted)

def format_for_web(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    便捷的Web格式化函数
    
    Args:
        data: 数据字典
        
    Returns:
        Web格式化字典
    """
    formatted = content_formatter.format_stream_data(data)
    return content_formatter.format_for_web(formatted)
