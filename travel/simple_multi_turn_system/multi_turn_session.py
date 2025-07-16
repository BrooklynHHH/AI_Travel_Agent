#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话会话管理模块
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger
from config import MAX_HISTORY_LENGTH, SESSION_TIMEOUT

logger = setup_logger(__name__)

class MultiTurnSession:
    """多轮对话会话管理器"""
    
    def __init__(self, session_id: str = None):
        """
        初始化会话
        
        Args:
            session_id: 会话ID，如果不提供则自动生成
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_input_history = []  # 用户输入历史
        self.conversation_history = []  # 完整对话历史
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
        self.metadata = {}  # 额外的元数据
        
        logger.info(f"创建新会话: {self.session_id}")
    
    def add_user_input(self, user_input: str) -> None:
        """
        添加用户输入到历史记录
        
        Args:
            user_input: 用户输入内容
        """
        if not user_input or not user_input.strip():
            logger.warning(f"会话 {self.session_id}: 尝试添加空的用户输入")
            return
        
        # 添加到用户输入历史
        input_record = {
            'content': user_input.strip(),
            'timestamp': datetime.now(),
            'turn_number': len(self.user_input_history) + 1
        }
        self.user_input_history.append(input_record)
        
        # 添加到完整对话历史
        self.conversation_history.append({
            'role': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.now()
        })
        
        # 维护历史长度限制
        if len(self.user_input_history) > MAX_HISTORY_LENGTH:
            removed = self.user_input_history.pop(0)
            logger.debug(f"会话 {self.session_id}: 移除旧的用户输入 (轮次 {removed['turn_number']})")
        
        # 更新活动时间
        self.last_activity = datetime.now()
        
        logger.info(f"会话 {self.session_id}: 添加用户输入 (轮次 {input_record['turn_number']}): {user_input[:50]}...")
    
    def add_system_response(self, response: str, agent_name: str = "system") -> None:
        """
        添加系统响应到历史记录
        
        Args:
            response: 系统响应内容
            agent_name: 响应的智能体名称
        """
        if not response or not response.strip():
            logger.warning(f"会话 {self.session_id}: 尝试添加空的系统响应")
            return
        
        # 添加到完整对话历史
        self.conversation_history.append({
            'role': 'assistant',
            'content': response.strip(),
            'agent_name': agent_name,
            'timestamp': datetime.now()
        })
        
        # 更新活动时间
        self.last_activity = datetime.now()
        
        logger.info(f"会话 {self.session_id}: 添加系统响应 ({agent_name}): {response[:50]}...")
    
    def get_user_input_history(self) -> List[str]:
        """
        获取用户输入历史列表
        
        Returns:
            用户输入内容列表
        """
        return [record['content'] for record in self.user_input_history]
    
    def get_conversation_context(self, max_turns: int = None) -> str:
        """
        获取对话上下文字符串
        
        Args:
            max_turns: 最大轮次数，None表示使用所有历史
            
        Returns:
            格式化的对话上下文
        """
        if not self.conversation_history:
            return ""
        
        # 确定要包含的历史范围
        history_to_use = self.conversation_history
        if max_turns and max_turns > 0:
            # 计算要包含的消息数量（每轮包含用户输入和系统响应）
            max_messages = max_turns * 2
            history_to_use = self.conversation_history[-max_messages:]
        
        # 构建上下文字符串
        context_parts = []
        for i, msg in enumerate(history_to_use, 1):
            role_label = "用户" if msg['role'] == 'user' else f"系统({msg.get('agent_name', 'assistant')})"
            context_parts.append(f"{i}. {role_label}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_latest_user_input(self) -> Optional[str]:
        """
        获取最新的用户输入
        
        Returns:
            最新的用户输入内容，如果没有则返回None
        """
        if self.user_input_history:
            return self.user_input_history[-1]['content']
        return None
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        获取会话摘要信息
        
        Returns:
            会话摘要字典
        """
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active,
            'user_input_count': len(self.user_input_history),
            'total_message_count': len(self.conversation_history),
            'duration_minutes': (self.last_activity - self.created_at).total_seconds() / 60,
            'metadata': self.metadata
        }
    
    def is_expired(self) -> bool:
        """
        检查会话是否已过期
        
        Returns:
            True如果会话已过期，False否则
        """
        if not self.is_active:
            return True
        
        expiry_time = self.last_activity + timedelta(seconds=SESSION_TIMEOUT)
        return datetime.now() > expiry_time
    
    def deactivate(self) -> None:
        """停用会话"""
        self.is_active = False
        logger.info(f"会话 {self.session_id} 已停用")
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        更新会话元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value
        self.last_activity = datetime.now()
        logger.debug(f"会话 {self.session_id}: 更新元数据 {key} = {value}")
    
    def clear_history(self) -> None:
        """清空会话历史"""
        old_count = len(self.conversation_history)
        self.user_input_history = []
        self.conversation_history = []
        self.last_activity = datetime.now()
        logger.info(f"会话 {self.session_id}: 清空历史记录 (原有 {old_count} 条消息)")

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.sessions: Dict[str, MultiTurnSession] = {}
        logger.info("会话管理器已初始化")
    
    def create_session(self, session_id: str = None) -> MultiTurnSession:
        """
        创建新会话
        
        Args:
            session_id: 指定的会话ID，如果不提供则自动生成
            
        Returns:
            新创建的会话对象
        """
        session = MultiTurnSession(session_id)
        self.sessions[session.session_id] = session
        logger.info(f"会话管理器: 创建会话 {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[MultiTurnSession]:
        """
        获取指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象，如果不存在则返回None
        """
        session = self.sessions.get(session_id)
        if session and session.is_expired():
            logger.info(f"会话管理器: 会话 {session_id} 已过期，自动移除")
            self.remove_session(session_id)
            return None
        return session
    
    def get_or_create_session(self, session_id: str = None) -> MultiTurnSession:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID，如果不提供则创建新会话
            
        Returns:
            会话对象
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        # 创建新会话
        return self.create_session(session_id)
    
    def remove_session(self, session_id: str) -> bool:
        """
        移除指定会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            True如果成功移除，False如果会话不存在
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"会话管理器: 移除会话 {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            清理的会话数量
        """
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
        
        if expired_sessions:
            logger.info(f"会话管理器: 清理了 {len(expired_sessions)} 个过期会话")
        
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """
        获取活跃会话数量
        
        Returns:
            活跃会话数量
        """
        return len([s for s in self.sessions.values() if s.is_active and not s.is_expired()])
    
    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        """
        获取所有会话的摘要信息
        
        Returns:
            会话摘要列表
        """
        return [session.get_session_summary() for session in self.sessions.values()]

# 全局会话管理器实例
session_manager = SessionManager()
